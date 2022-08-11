from datetime import timedelta
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from django.db import transaction
from rest_framework import fields
from rest_framework import serializers
from client.fields import ModelField
from client.models import Client, Review
from delivery.settings import ADDITIONAL_DELIVERY_TIME_PER_METER, DELIVERY_COST_PER_METER

from merchant.models import Delivery, Menu, MenuCategory, MenuItem, MenuItemOption, MenuItemOptionGroup, Order, OrderItem, OrderItemOption, OrderItemOptionGroup, Restaurant, SelfPickup
from merchant.serializers import PriceAdjustmentSerializer
from merchant.utils import calc_delivery_cost, calc_distance_from_coords, round_to_base
from rider.models import Rider, Session


class RestaurantListSerializer(serializers.ModelSerializer):
    distance = serializers.SerializerMethodField('calc_distance')
    delivery_cost = serializers.SerializerMethodField('calc_delivery_cost')
    delivery_time = serializers.SerializerMethodField('calc_delivery_time')

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'distance', 'delivery_cost', 'delivery_time', 'rating']
    
    def validate(self, attrs):
        try:
            self.user_latitude = float(self.context.get('request').query_params.get('user_latitude'))
            self.user_longitude = float(self.context.get('request').query_params.get('user_longitude'))
        except:
            raise serializers.ValidationError('Invalid latitude or longitude!')
        return attrs
        
    def calc_distance(self, obj):
        restaurant_latitude = float(obj.latitude)
        restaurant_longitude = float(obj.longitude)
        user_latitude = float(self.context.get('request').query_params.get('user_latitude'))
        user_longitude = float(self.context.get('request').query_params.get('user_longitude'))
        dist = calc_distance_from_coords(user_latitude, user_longitude, restaurant_latitude, restaurant_longitude)
        return round(dist)
    
    def calc_delivery_cost(self, obj):
        return round(self.calc_distance(obj) * DELIVERY_COST_PER_METER, 1)
    
    def calc_delivery_time(self, obj):
        delivery_time = timedelta(minutes=20 + self.calc_distance(obj) * ADDITIONAL_DELIVERY_TIME_PER_METER) 
        return delivery_time + obj.order_fulfillment_time


class ClientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.get_full_name')
    
    class Meta:
        model = Client
        fields = ['id', 'name']


class ReviewSerializer(serializers.ModelSerializer):
    client = ClientSerializer()

    class Meta:
        model = Review
        fields = ['client', 'rating', 'text', 'created']
        

class MenuItemOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItemOption 
        fields = ['id', 'name']


class MenuItemOptionGroupSerializer(serializers.ModelSerializer):
    options = MenuItemOptionSerializer(many=True)
    class Meta:
        model = MenuItemOptionGroup
        fields = ['id', 'name', 'type', 'options']


class MenuItemDetailSerializer(serializers.ModelSerializer):
    option_groups = MenuItemOptionGroupSerializer(many=True)
    
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'price', 'option_groups']


class MenuItemListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'price']


class MenuCategorySerializer(serializers.ModelSerializer):
    items = MenuItemListSerializer(many=True)
    
    class Meta:
        model = MenuCategory
        fields = ['id', 'name', 'items']


class MenuSerializer(serializers.ModelSerializer):
    categories = MenuCategorySerializer(many=True)

    class Meta:
        model = Menu
        fields = ['id', 'name', 'categories']


class RestaurantDetailSerializer(serializers.ModelSerializer):
    distance = serializers.SerializerMethodField('calc_distance_with_rounding')
    delivery_cost = serializers.SerializerMethodField('calc_delivery_cost')
    delivery_time = serializers.SerializerMethodField('calc_delivery_time')
    current_menu = MenuSerializer()

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'distance', 'delivery_cost', 'delivery_time', 'rating', 'current_menu']
        
    def _calc_distance(self, obj):
        try:
            user_latitude = float(self.context.get('request').query_params.get('user_latitude'))
            user_longitude = float(self.context.get('request').query_params.get('user_longitude'))
        except:
            raise serializers.ValidationError('Invalid latitude or longitude')
        restaurant_latitude = float(obj.latitude)
        restaurant_longitude = float(obj.longitude)
        return calc_distance_from_coords(user_latitude, user_longitude, restaurant_latitude, restaurant_longitude)
    
    def calc_distance_with_rounding(self, obj):
        return round(self._calc_distance(obj), 1)
    
    def calc_delivery_cost(self, obj):
        return round(self._calc_distance(obj) * 2, 1)
    
    def calc_delivery_time(self, obj):
        return round_to_base(20 + self._calc_distance(obj) * 60 / 20, 5)


class OrderItemOptionListSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(method_name='get_id', read_only=True)
    name = serializers.SerializerMethodField(method_name='get_name', read_only=True)
    
    class Meta:
        model = OrderItemOption
        fields = ['id', 'name']
    
    def get_id(self, obj):
        return obj.menu_item_option.id
    
    def get_name(self, obj):
        return obj.menu_item_option.name


class OrderItemOptionGroupListSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(method_name='get_id', read_only=True)
    name = serializers.SerializerMethodField(method_name='get_name', read_only=True)
    options = OrderItemOptionListSerializer(many=True)
    
    class Meta:
        model = OrderItemOptionGroup
        fields = ['id', 'name', 'options']

    def get_id(self, obj):
        return obj.menu_item_option_group.id
    
    def get_name(self, obj):
        return obj.menu_item_option_group.name
        

class OrderItemListSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(method_name='get_id', read_only=True)
    instance_id = serializers.IntegerField(source='id')
    name = serializers.SerializerMethodField(method_name='get_name', read_only=True)
    option_groups = OrderItemOptionGroupListSerializer(many=True)
    price_adjustment = PriceAdjustmentSerializer()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'instance_id', 'name', 'price', 'quantity', 'option_groups', 'price_adjustment']

    def get_id(self, obj):
        return obj.menu_item.id

    def get_name(self, obj):
        return obj.menu_item.name


class OrderListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['id', 'restaurant', 'type', 'created', 'status', 'price']


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemListSerializer(many=True)
    estimated_completion_datetime = serializers.SerializerMethodField(method_name='get_estimated_completion_datetime')

    class Meta:
        model = Order
        fields = ['id', 'restaurant', 'type', 'items', 'created', 'status', 'price', 'estimated_completion_datetime']
    
    def get_estimated_completion_datetime(self, obj):
        if obj.type == Order.DELIVERY:
            return obj.delivery.estimated_delivery_datetime
        else:
            return obj.self_pickup.estimated_pickup_datetime


class OrderItemOptionCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=MenuItemOption.objects.all(), source='menu_item_option')
    
    class Meta:
        model = OrderItemOption
        fields = ['id']


class OrderItemOptionGroupCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=MenuItemOptionGroup.objects.all(), source='menu_item_option_group')
    options = OrderItemOptionCreateSerializer(many=True)
    
    class Meta:
        model = OrderItemOptionGroup
        fields = ['id', 'options']
        

class OrderItemCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all(), source='menu_item')
    option_groups = OrderItemOptionGroupCreateSerializer(many=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'option_groups', 'quantity']


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'client', 'restaurant', 'created', 'items']
        extra_kwargs = {
            'id': {'read_only': True},
        }
    
    def validate_restaurant(self, restaurant):
        if not restaurant.is_open:
            raise serializers.ValidationError('Restaurant is closed')
        return restaurant

    @transaction.atomic
    def create(self, validated_data):
        order = Order.objects.create(
            client=validated_data['client'], 
            restaurant=validated_data['restaurant'], 
            created=timezone.now(),
        )
        for item_data in validated_data['items']:
            order_item = OrderItem.objects.create(
                menu_item=item_data['menu_item'], 
                order=order
            )
            for option_group_data in item_data['option_groups']:
                order_item_option_group = OrderItemOptionGroup.objects.create(
                    menu_item_option_group=option_group_data['menu_item_option_group'],
                    order_item=order_item
                )
                for option_data in option_group_data['options']:
                    OrderItemOption.objects.create(
                        menu_item_option=option_data['menu_item_option'],
                        order_item_option_group=order_item_option_group
                    )
        return order


class SelfPickupOrderCreateSerializer(OrderCreateSerializer):
    estimated_pickup_datetime = serializers.SerializerMethodField(method_name='get_estimated_pickup_datetime')

    class Meta(OrderCreateSerializer.Meta):
        fields = OrderCreateSerializer.Meta.fields + ['estimated_pickup_datetime']
        extra_kwargs = OrderCreateSerializer.Meta.extra_kwargs
    
    def get_estimated_pickup_datetime(self, obj):
        return obj.self_pickup.estimated_pickup_datetime
    
    @transaction.atomic
    def create(self, validated_data):
        order = super().create(validated_data)
        SelfPickup.objects.create(
            order=order, 
            estimated_pickup_datetime=timezone.now() + order.restaurant.order_fulfillment_time
        )
        return order
 

class RiderSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(method_name='get_name')
    session = serializers.SerializerMethodField(method_name='get_session')
        
    class Meta:
        model = Rider
        fields = ['id', 'name', 'session']
    
    def get_name(self, obj):
        return obj.user.name
    
    def get_session(self, obj):
        return obj.current_session.id


class DeliveryOrderCreateSerializer(OrderCreateSerializer):
    rider_session = ModelField(model=Session, source='delivery.session', read_only=True)
    user_latitude = serializers.DecimalField(decimal_places=7, max_digits=9, write_only=True)
    user_longitude = serializers.DecimalField(decimal_places=7, max_digits=10, write_only=True)
    estimated_delivery_datetime = serializers.SerializerMethodField(
        method_name='get_estimated_delivery_datetime'
    )
    delivery_cost = serializers.SerializerMethodField(method_name='get_delivery_cost')
    
    class Meta(OrderCreateSerializer.Meta):
        fields = OrderCreateSerializer.Meta.fields \
            + ['estimated_delivery_datetime', 'rider_session', 'delivery_cost', 
               'user_latitude', 'user_longitude']

    def get_estimated_delivery_datetime(self, obj):
        return obj.delivery.estimated_delivery_datetime

    def get_delivery_cost(self, obj):
        return obj.delivery.delivery_cost
    
    @transaction.atomic
    def create(self, validated_data):
        order = super().create(validated_data)

        delivery_cost = calc_delivery_cost(
            order.restaurant, 
            user_latitude=validated_data['user_latitude'], 
            user_longitude=validated_data['user_longitude']
        )
        estimated_delivery_datetime = timezone.now() + order.restaurant.order_fulfillment_time
        Delivery.objects.create(
            order=order, 
            delivery_cost=delivery_cost,
            estimated_delivery_datetime=estimated_delivery_datetime
        )
        return order
