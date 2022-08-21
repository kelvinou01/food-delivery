
from djangochannelsrestframework.permissions import IsAuthenticated
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer import model_observer
from djangochannelsrestframework.decorators import action
import base64
from django.contrib.auth import authenticate as django_authenticate
from channels.db import database_sync_to_async
from channels.exceptions import DenyConnection
from client.serializers import OrderDetailSerializer
from merchant.models import Order, Restaurant


class OrderConsumer(GenericAsyncAPIConsumer):
    permission_classes = [IsAuthenticated]

    async def websocket_connect(self, event):
        @database_sync_to_async
        def authenticate(username, password):
            return django_authenticate(username=username, password=password)
            
        @database_sync_to_async
        def get_restaurant(id):
            return Restaurant.objects.get(id=id)

        @database_sync_to_async
        def restaurant_belongs_to_user(user, restaurant):
            if hasattr(self.user, 'merchant'):
                if self.user.merchant.restaurant == self.restaurant:
                    return True
            return False
            
        auth_header = (header[1] for header in self.scope['headers'] if header[0] == b'authorization')
        auth_header = next(auth_header, None)

        if auth_header is None:
            raise DenyConnection('Must include authorization header')
        
        credentials = auth_header[6:]
        username, password = base64.b64decode(credentials).decode().split(':')
        self.user = await authenticate(username, password)

        try:
            self.restaurant = await get_restaurant(id=self.scope['url_route']['kwargs']['restaurant_id'])
        except Restaurant.DoesNotExist:
            raise DenyConnection()

        if not await restaurant_belongs_to_user(self.user, self.restaurant):
            raise DenyConnection()
        
        return await super().websocket_connect(event)

    @model_observer(Order)
    async def order_activity(
        self,
        message: OrderDetailSerializer,
        observer=None,
        subscribing_request_ids=[],
        **kwargs
    ):
        await self.send_json(message)

    @order_activity.serializer
    def order_activity(self, instance: Order, action, **kwargs) -> OrderDetailSerializer:
        return OrderDetailSerializer(instance).data

    @order_activity.groups_for_signal
    def order_activity(self, instance: Order, **kwargs):
        # NOTE: this block of code is called very often *DO NOT make DB QUERIES HERE*
        yield f"-restaurant__{instance.restaurant_id}"

    @order_activity.groups_for_consumer
    def order_activity(self, school=None, classroom=None, **kwargs):
        yield f"-restaurant__{kwargs['restaurant_id']}"

    @action()
    async def subscribe_to_order_activity(self, request_id, **kwargs):
        await self.order_activity.subscribe(request_id=request_id, restaurant_id=self.restaurant.id)
