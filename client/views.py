from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from rest_framework import views
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from client.models import Review
from client.permissions import IsClient
from client.serializers import ClientRegisterSerializer, DeliveryOrderCreateSerializer, MenuItemDetailSerializer, OrderDetailSerializer, ReviewSerializer, SelfPickupOrderCreateSerializer, OrderListSerializer, RestaurantDetailSerializer, RestaurantListSerializer
from delivery import settings
from delivery.views import BaseRegister
from merchant.models import MenuItem, Order, Restaurant


class Register(BaseRegister):
    serializer_class = ClientRegisterSerializer


class RestaurantList(generics.ListAPIView):
    # TODO: Sort by closest
    # TODO: Cache, page, limit.
    permission_classes = [IsAuthenticated, IsClient]
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantListSerializer
    # filter_backends = [filters.SearchFilter]
    # search_fields = ["name"]

    def list(self, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    
class RestaurantDetail(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsClient]
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantDetailSerializer
    lookup_url_kwarg = 'restaurant_id'


class ReviewList(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsClient]
    serializer_class = ReviewSerializer
    lookup_url_kwarg = 'restaurant_id'

    def get_queryset(self):
        return Review.objects.filter(restaurant=self.kwargs['restaurant_id'])


class ReviewCreate(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsClient] 
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    lookup_url_kwarg = 'restaurant_id'

    def post(self, *args, **kwargs):
        order = Order.objects.get(id=self.kwargs['order_id'])
        if order.created >= timezone.now() - timedelta(days=5):
            return Response(
                status=status.HTTP_400_BAD_REQUEST, 
                data={'Cannot review based on order created more than 5 days ago.'}
            )

        reviews = Review.objects.filter(client=order.client, restaurant=order.restaurant)
        if reviews.exists():
            return Response(
                status=status.HTTP_400_BAD_REQUEST, 
                data={'Client has already reviewed the restaurant.'}
            )
        
        return super().post(*args, **kwargs)
    

class MenuItemDetail(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsClient]
    serializer_class = MenuItemDetailSerializer
    lookup_url_kwarg = 'menu_item_id'

    def get_queryset(self):
        return MenuItem.objects.filter(menu_category__menu__restaurant=self.kwargs['restaurant_id'])


class OrderList(generics.ListAPIView):
    # TODO: Use auth header user client id instead of request body client id
    permission_classes = [IsAuthenticated, IsClient]
    serializer_class = OrderListSerializer

    def get_queryset(self):
        return Order.objects.filter(client=self.request.user.client)


class OrderDetail(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsClient]
    serializer_class = OrderDetailSerializer
    lookup_url_kwarg = 'order_id'

    def get_queryset(self):
        return Order.objects.filter(client=self.request.user.client)


class DeliveryOrderCreate(generics.CreateAPIView):
    # TODO: Use auth header user client id instead of request body client id
    permission_classes = [IsAuthenticated, IsClient]
    serializer_class = DeliveryOrderCreateSerializer

    def get_queryset(self):
        return Order.objects.filter(client=self.request.user.client)


class SelfPickupOrderCreate(generics.CreateAPIView):
    # TODO: Use auth header user client id instead of request body client id
    permission_classes = [IsAuthenticated, IsClient]
    serializer_class = SelfPickupOrderCreateSerializer

    def get_queryset(self):
        return Order.objects.filter(client=self.request.user.client) 


class OrderCancel(views.APIView):
    permission_classes = [IsAuthenticated, IsClient]  # TODO: OwnsOrder permission
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(id=self.kwargs['order_id'])
            order.cancel(reason=self.request.data.get('reason'))
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': e.message}) 
        
        # TODO: Notify restaurant

        # TODO: Notify rider    

        return Response(status=status.HTTP_200_OK)


class OrderComplete(views.APIView):
    permission_classes = [IsAuthenticated, IsClient]  # TODO: OwnsOrder, OrderIsSelfPickup
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(id=self.kwargs.get('order_id'))
            order.complete()
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': e.message}) 
        
        # TODO: Notify restaurant
        
        # TODO: Notify rider

        return Response(status=status.HTTP_200_OK)
