from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework import views
from django.core.exceptions import ValidationError
from django.db import transaction
from client.serializers import OrderDetailSerializer

from merchant.models import Holiday, MenuHours, MenuItem, Order, PauseHours, Restaurant, Menu
from merchant.permissions import IsRestaurantStaff, OrderIsForRestaurant, OrderItemIsInOrder
from merchant.serializers import HolidaySerializer, MenuDetailSerializer, MenuHoursSerializer, \
    MenuListSerializer, MenuItemListSerializer, MenuItemDetailSerializer, OrderCancelSerializer, \
    OrderDelaySerializer, OrderListSerializer, PriceAdjustmentSerializer, RestaurantSerializer, RegisterSerializer, \
    StatusSerializer


class RestaurantCreate(generics.CreateAPIView):
    permission_classes = []
    serializer_class = RestaurantSerializer
    

class MenuListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsRestaurantStaff]

    def get_queryset(self):
        restaurant = self.request.user.restaurantstaff.restaurant
        return Menu.objects.filter(restaurant=restaurant)
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MenuListSerializer
        else:
            return MenuDetailSerializer


class MenuDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsRestaurantStaff]
    serializer_class = MenuDetailSerializer
    lookup_url_kwarg = 'menu_id'

    def get_queryset(self):
        restaurant = self.request.user.restaurantstaff.restaurant
        return Menu.objects.filter(restaurant=restaurant)
    
    def post(self, request, *args, **kwargs):
        user_restaurant = self.request.user.restaurantstaff.restaurant
        request_restaurant = Restaurant.objects.get(id=request.data['restaurant'])
        if user_restaurant != request_restaurant:
            return Response(code=404)
        return super().post(request, *args, **kwargs)


class MenuItemsListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsRestaurantStaff]

    def get_queryset(self):
        restaurant = self.request.user.restaurantstaff.restaurant
        menu = self.kwargs['menu_id']
        return MenuItem.objects.filter(menu_category__menu_id=menu, 
                                       menu_category__menu__restaurant=restaurant)
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MenuItemListSerializer
        else:
            return MenuItemDetailSerializer


class MenuItemDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsRestaurantStaff]
    serializer_class = MenuItemDetailSerializer
    lookup_url_kwarg = 'item_id'

    def get_queryset(self):
        restaurant = self.request.user.restaurantstaff.restaurant
        menu = self.kwargs['menu_id']
        return MenuItem.objects.filter(menu_category__menu_id=menu, 
                                       menu_category__menu__restaurant=restaurant)


class MenuHoursListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsRestaurantStaff]
    serializer_class = MenuHoursSerializer

    def get_queryset(self):
        restaurant = self.request.user.restaurantstaff.restaurant
        return MenuHours.objects.filter(menu__restaurant=restaurant)
    
    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # NOTE: Every post request is an overwrite of the restaurant's MenuHours.
                menu_hours = self.get_queryset()
                menu_hours.delete()
                serializer = self.get_serializer(data=request.data, many=True)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
        except ValidationError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, 
                            data={e.message})
        
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

 
class OrderList(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsRestaurantStaff]
    serializer_class = OrderListSerializer

    def get_queryset(self):
        # TODO: Query param open=true -> Filter by unfulfilled orders
        # TODO: Add websocket
        restaurant = self.request.user.restaurantstaff.restaurant
        return Order.objects.filter(restaurant=restaurant)


class OrderDetail(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsRestaurantStaff]
    serializer_class = OrderDetailSerializer
    lookup_url_kwarg = 'order_id'

    def get_queryset(self):
        restaurant = self.request.user.restaurantstaff.restaurant
        return Order.objects.filter(restaurant=restaurant) 


class Status(views.APIView):
    permission_classes = [IsAuthenticated, IsRestaurantStaff]
    serializer_class = StatusSerializer

    def get_serializer_context(self):
        return {
            'view': self
        }

    def get(self, request, *args, **kwargs):
        restaurant = Restaurant.objects.get(id=self.kwargs['restaurant_id'])
        current_datetime = timezone.now()
        
        if not restaurant.is_open_according_to_regular_menu_hours:
            data = {
                'status': StatusSerializer.CLOSED,
            }
        elif restaurant.is_on_holiday:
            data = {
                'status': StatusSerializer.ON_HOLIDAY, 
            }
        elif restaurant.is_paused:
            pause_hours = PauseHours.objects.get(
                restaurant=self.kwargs['restaurant_id'], 
                start_datetime__lte=current_datetime, 
                end_datetime__gt=current_datetime
            )
            data = {
                'status': StatusSerializer.PAUSED, 
                'pause_reason': pause_hours.reason, 
                'paused_until': pause_hours.end_datetime
            }
        else:
            data = {
                'status': StatusSerializer.ONLINE, 
            }
    
        return Response(data=data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, 
                                           context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data['status'] == StatusSerializer.PAUSED:
            try:
                current_pause_hours = PauseHours.objects.get(
                    start_datetime__lte=timezone.now(), 
                    end_datetime__gt=timezone.now(), 
                    restaurant=self.kwargs['restaurant_id']
                )
                current_pause_hours.end_datetime = serializer.validated_data['paused_until']
                current_pause_hours.save()
            except PauseHours.DoesNotExist:
                serializer.save()

        elif serializer.validated_data['status'] == StatusSerializer.ONLINE:
            try:
                restaurant = Restaurant.objects.get(id=self.kwargs['restaurant_id'])
                current_pause_hours = PauseHours.objects.get(
                    start_datetime__lte=timezone.now(), 
                    end_datetime__gt=timezone.now(), 
                    restaurant=restaurant
                )
                current_pause_hours.end_datetime = timezone.now()
                current_pause_hours.save()
            except PauseHours.DoesNotExist:
                pass 
            
        return Response(status=status.HTTP_200_OK)


class HolidayListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsRestaurantStaff]
    serializer_class = HolidaySerializer

    def get_queryset(self):
        return Holiday.objects.filter(restaurant=self.kwargs['restaurant_id'],
                                      end_datetime__gte=timezone.now())

    def create(self, request, *args, **kwargs):
        # Create many by default, by setting many=True for get_serializer
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class HolidayDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsRestaurantStaff]
    serializer_class = HolidaySerializer
    lookup_url_kwarg = 'holiday_id'
    
    def get_queryset(self):
        return Holiday.objects.filter(restaurant=self.kwargs['restaurant_id'], 
                                      end_datetime__gte=timezone.now())


class OrderFinishCooking(views.APIView):
    permission_classes = [IsAuthenticated, IsRestaurantStaff, OrderIsForRestaurant]
    
    def post(self, request, *args, **kwargs):
        # Order must exist, because OrderIsForRestaurant
        order = Order.objects.get(
            id=self.kwargs['order_id'], 
            restaurant=self.request.user.restaurantstaff.restaurant
        )
        try:
            order.finish_cooking()
        except ValidationError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={e.message})
        return Response(status=status.HTTP_200_OK)
        

class OrderCancel(views.APIView):
    permission_classes = [IsAuthenticated, IsRestaurantStaff, OrderIsForRestaurant]
    serializer_class = OrderCancelSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Order must exist, because OrderIsForRestaurant
        order = Order.objects.get(
            id=self.kwargs['order_id'], 
            restaurant=self.request.user.restaurantstaff.restaurant
        )
        try:
            order.cancel(reason=serializer.validated_data['reason'])
        except ValidationError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={e.message})
        return Response(status=status.HTTP_200_OK)


class OrderDelay(views.APIView):
    permission_classes = [IsAuthenticated, IsRestaurantStaff, OrderIsForRestaurant]
    serializer_class = OrderDelaySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Order must exist, because OrderIsForRestaurant
        order = Order.objects.get(
            id=self.kwargs['order_id'], 
            restaurant=self.request.user.restaurantstaff.restaurant
        )
        try:
            order.delay(serializer.validated_data['delay_by'])
        except ValidationError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={e.message})
        return Response(status=status.HTTP_200_OK)


class PriceAdjustment(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsRestaurantStaff, 
                          OrderIsForRestaurant, OrderItemIsInOrder]
    serializer_class = PriceAdjustmentSerializer
