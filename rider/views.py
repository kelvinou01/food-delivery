from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from rest_framework import views
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from delivery.views import BaseRegister

from merchant.models import Order
from merchant.serializers import OrderCancelSerializer
from rider.mixins import CurrentSessionMixin
from rider.models import Session
from rider.permissions import IsDeliveringThisOrder, IsRider, RiderOwnsSession
from rider.serializers import OrderDetailSerializer, OrderListSerializer, RiderRegisterSerializer, \
    SessionCreateSerializer, SessionExtendSerializer, SessionListSerializer

    
class RiderRegister(BaseRegister):
    serializer_class = RiderRegisterSerializer


class SessionListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsRider]
    
    def get_queryset(self):
        return Session.objects.filter(rider=self.request.user.rider)
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SessionListSerializer
        else:
            return SessionCreateSerializer 


class CurrentSessionEnd(views.APIView, CurrentSessionMixin):
    permission_classes = [IsAuthenticated, IsRider]

    def post(self, request, *args, **kwargs):
        # TODO: Check if the rider has finished their last order
        session = self.get_current_session()
        if session is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'No session currently active'})
        session.end_datetime = timezone.now()
        session.save()
        return Response(status=status.HTTP_200_OK)

 
class CurrentSessionExtend(views.APIView, CurrentSessionMixin):
    permission_classes = [IsAuthenticated, IsRider]
    serializer_class = SessionExtendSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = self.get_current_session()
        if session is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'No session currently active'})

        session.end_datetime = serializer.validated_data['end_datetime']
        session.save()
        return Response(status=status.HTTP_200_OK)


class CurrentSessionOrderList(generics.ListAPIView, CurrentSessionMixin):
    permission_classes = [IsAuthenticated, IsRider]
    serializer_class = OrderListSerializer

    def get_queryset(self):
        session = self.get_current_session()
        if session is None:
            return Order.object.empty()

        return Order.objects.filter(
            delivery__isnull=False,
            delivery__session=session, 
        )


class SessionOrderList(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsRider, RiderOwnsSession]
    serializer_class = OrderListSerializer

    def get_queryset(self):
        return Order.objects.filter(
            delivery__isnull=False,
            delivery__session_id=self.kwargs['session_id'], 
        )


class OrderList(generics.ListAPIView):
    # TODO: Sort by closest Restaurant
    # TODO: Cache, page, limit.
    permission_classes = [IsAuthenticated, IsRider]
    serializer_class = OrderListSerializer

    def get_queryset(self):
        delivery_orders_searching_for_rider = Order.objects.filter(
            cancellation__isnull=True,
            completed__isnull=True,
            delivery__isnull=False, 
            delivery__session__isnull=True
        )
        return delivery_orders_searching_for_rider


class OrderDetail(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsRider, IsDeliveringThisOrder]
    serializer_class = OrderDetailSerializer
    lookup_url_kwarg = 'order_id'

    def get_queryset(self):
        session = self.request.user.rider.current_session
        delivery_orders_fulfilled_by_rider = Order.objects.filter(
            delivery__isnull=False, 
            delivery__session = session
        )
        return delivery_orders_fulfilled_by_rider


class OrderAccept(views.APIView):
    permission_classes = [IsAuthenticated, IsRider]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        order = Order.objects.get(id=self.kwargs['order_id'])
        order.delivery.session = self.request.user.rider.current_session
        order.delivery.estimated_delivery_datetime = timezone.now()
        order.delivery.save()
        return Response(status=status.HTTP_200_OK)


class OrderPickup(views.APIView):
    permission_classes = [IsAuthenticated, IsRider]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        order = Order.objects.get(id=self.kwargs['order_id'])
        try:
            order.delivery.pick_up()
        except ValidationError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={e.message})
        return Response(status=status.HTTP_200_OK)


class OrderComplete(views.APIView):
    permission_classes = [IsAuthenticated, IsRider]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        order = Order.objects.get(id=self.kwargs['order_id'])
        try:
            order.complete()
        except ValidationError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={e.message})
        return Response(status=status.HTTP_200_OK)


class OrderCancel(views.APIView):
    permission_classes = [IsAuthenticated, IsRider]
    serializer_class = OrderCancelSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = Order.objects.get(id=self.kwargs['order_id'])
        try:
            order.cancel(reason=serializer.validated_data['reason'])
        except ValidationError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={e.message})
        return Response(status=status.HTTP_200_OK)
