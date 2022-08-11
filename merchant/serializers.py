from datetime import timedelta
from wsgiref import validate
from django.utils import timezone
from django.core.exceptions import ValidationError as ModelValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError, transaction

from merchant.models import Holiday, Menu, MenuCategory, MenuHours, MenuItem, MenuItemOption, MenuItemOptionGroup, Order, OrderCancellation, OrderItemPriceAdjustment, PauseHours, Restaurant, RestaurantStaff

class RestaurantSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Restaurant
        fields = ['name', 'address', 'latitude', 'longitude']
    
    @transaction.atomic
    def create(self, validated_data):
        restaurant = Restaurant.objects.create(
            name=validated_data['name'], address=validated_data['address'], 
            latitude=validated_data['latitude'], longitude=validated_data['longitude']
        )
        RestaurantStaff.objects.create(
            user=self.context.get('request').user, restaurant=restaurant
        )
        return restaurant

class MenuHoursSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MenuHours
        fields = ['id', 'day_of_the_week', 'start_time', 'end_time', 'menu']


class MenuItemListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'price']
        

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


class MenuCategorySerializer(serializers.ModelSerializer):

    items = MenuItemDetailSerializer(many=True)
    class Meta:
        model = MenuCategory
        fields = ['id', 'name', 'items']


class MenuDetailSerializer(serializers.ModelSerializer):
    categories = MenuCategorySerializer(many=True)
    hours = MenuHoursSerializer()

    class Meta:
        model = Menu
        fields = ['id', 'name', 'restaurant', 'categories', 'hours']
    
    def get_hours(self, obj):
        result = {
            MenuHours.MONDAY: [], 
            MenuHours.TUESDAY: [], 
            MenuHours.WEDNESDAY: [], 
            MenuHours.THURSDAY: [], 
            MenuHours.FRIDAY: [], 
            MenuHours.SATURDAY: [], 
            MenuHours.SUNDAY: [], 
        }
        
        for menu_hours in MenuHours.objects.filter(menu=obj):
            result[menu_hours.day_of_the_week] = (menu_hours.start_time, menu_hours.end_time)

    @transaction.atomic
    def create(self, validated_data):
        menu = Menu.objects.create(
            name=validated_data['name'],
            restaurant=validated_data['restaurant']
        )
        for menu_category_data in validated_data['categories']:
            menu_category = MenuCategory.objects.create(
                name=menu_category_data['name'],
                menu=menu
            )
            for menu_item_data in menu_category_data['items']:
                menu_item = MenuItem.objects.create(
                    name=menu_item_data['name'],
                    price=menu_item_data['price'],
                    menu_category=menu_category
                )
                for menu_item_option_group_data in menu_item_data['option_groups']:
                    menu_item_option_group = MenuItemOptionGroup.objects.create(
                        name=menu_item_option_group_data['name'],
                        type=menu_item_option_group_data['type'],
                        menu_item=menu_item
                    )
                    for menu_item_option_data in menu_item_option_group_data['options']:
                        menu_item_option = MenuItemOption.objects.create(
                            name=menu_item_option_data['name'],
                            option_group=menu_item_option_group
                        )
        return menu


class MenuListSerializer(serializers.ModelSerializer):
    menu_hours = MenuHoursSerializer(many=True)

    class Meta:
        model = Menu
        fields = ['id', 'name', 'menu_hours']


class OrderListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Order
        fields = ['id', 'client', 'created', 'completed', 'status', 'type']
        extra_kwargs = {
            'id': {'read_only': True},
            'completed': {'read_only': True},
            'status': {'read_only': True},
        }


class StatusSerializer(serializers.Serializer):
    ONLINE = 'ONLINE'
    CLOSED = 'CLOSED'
    ON_HOLIDAY = 'ON_HOLIDAY'
    PAUSED = 'PAUSED'
    # Only allow merchant to post PAUSED and ONLINE. 
    STATUS_CHOICES = [(PAUSED, 'Paused'), (ONLINE, 'Online')]

    status = serializers.ChoiceField(choices=STATUS_CHOICES)
    paused_reason = serializers.CharField()
    paused_until = serializers.DateTimeField(required=False)
    
    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs['status'] == StatusSerializer.PAUSED and not attrs['paused_until']:
            raise ValidationError('Pause request must include paused_until datetime')
        if attrs['paused_until'] < timezone.now():
            raise ValidationError('Invalid paused_until')
        return attrs
                
    def create(self, validated_data):
        restaurant = Restaurant.objects.get(id=self.context['view'].kwargs['restaurant_id'])
        return PauseHours.objects.create(
            start_datetime=timezone.now(), 
            end_datetime=validated_data['paused_until'], 
            reason=validated_data['paused_reason'], 
            restaurant=restaurant
        )

class HolidaySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Holiday
        fields = ['id', 'restaurant', 'start_datetime', 'end_datetime']
        extra_kwargs = {
            'id': {'read_only': True},
            'restaurant': {'read_only': True}
        }

    def create(self, validated_data):
        restaurant = Restaurant.objects.get(id=self.context['view'].kwargs['restaurant_id'])
        return Holiday.objects.create(
            start_datetime=validated_data['start_datetime'], 
            end_datetime=validated_data['end_datetime'], 
            restaurant=restaurant
        )


class OrderCancelSerializer(serializers.Serializer):
    reason = serializers.CharField(min_length=10, max_length=200)


class OrderDelaySerializer(serializers.Serializer):
    delay_by = serializers.DurationField()


class PriceAdjustmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItemPriceAdjustment    
        fields = ['adjustment', 'reason']
    
    def create(self, validated_data):
        try:
            return OrderItemPriceAdjustment.objects.create(
                adjustment=validated_data['adjustment'], 
                reason=validated_data['reason'], 
                order_item_id=self.context['view'].kwargs['order_item_id']
            )
        except IntegrityError:
            raise ValidationError('The price of an item can only be adjusted once')

