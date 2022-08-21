from datetime import timedelta
from django.utils import timezone
from functools import cached_property
from django.db import models
from django.db import transaction
from django.core.exceptions import ValidationError

from client.models import Review
    

class MenuHours(models.Model):
    # MenuHours is the single source of truth of a restaurant's *regular* opening hours
    menu = models.ForeignKey('Menu', on_delete=models.CASCADE, 
                             related_name='menu_hours')
    
    start_time = models.TimeField()
    end_time = models.TimeField()

    # Follow `datetime` convention: https://docs.python.org/3/library/datetime.html#datetime.datetime.weekday
    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = range(7)
    DAYS_OF_THE_WEEK = [
        (MONDAY, 'Monday'),
        (TUESDAY, 'Tuesday'),
        (WEDNESDAY, 'Wednesday'),
        (THURSDAY, 'Thursday'),
        (FRIDAY, 'Friday'),
        (SATURDAY, 'Saturday'),
        (SUNDAY, 'Sunday'),
    ]

    day_of_the_week = models.PositiveSmallIntegerField(choices=DAYS_OF_THE_WEEK)

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError('start_time must be earlier than end_time')

        overlapping_menu_hours = MenuHours.objects.filter(
            menu__restaurant=self.menu.restaurant, 
            day_of_the_week=self.day_of_the_week,
            start_time__lt=self.end_time, 
            end_time__gt=self.start_time
        ).exclude(id=self.id)
        if overlapping_menu_hours.exists():
            raise ValidationError('Cannot save overlapping menu hours')
    
    def __str__(self):
        restaurant = str(self.menu.restaurant)
        menu = str(self.menu)
        day = self.get_day_of_the_week_display()
        start_time = str(self.start_time)
        end_time = str(self.end_time)
        return f'{restaurant} ({menu}) on {day}: {start_time} - {end_time}'


class Holiday(models.Model):
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, 
                                   related_name='holidays')

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    def clean(self):
        if self.start_datetime >= self.end_datetime:
            raise ValidationError('start_datetime must be earlier than end_datetime')

        overlapping_holiday_hours = Holiday.objects.filter(
            restaurant=self.restaurant, 
            start_datetime__lt=self.end_datetime, 
            end_datetime__gt=self.start_datetime
        )
        if overlapping_holiday_hours.exists():
            raise ValidationError('Cannot save overlapping holiday hours')


class PauseHours(models.Model):
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, 
                                   related_name='pause_hours')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    reason = models.CharField(max_length=200, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    def clean(self):
        if self.start_datetime >= self.end_datetime:
            raise ValidationError('start_time must be earlier than end_time')

        overlapping_pause_hours = PauseHours.objects.filter(
            restaurant=self.restaurant, 
            start_datetime__lt=self.end_datetime, 
            end_datetime__gt=self.start_datetime
        ).exclude(id=self.id)
        if overlapping_pause_hours.exists():
            raise ValidationError('Cannot save overlapping pause hours')


class Restaurant(models.Model):
    name = models.CharField(max_length=100) 
    address = models.CharField(max_length=300)
    is_live = models.BooleanField(default=False)

    # TODO: Use PostGIS, which allows fast querying of restaurants within a certain radius of any point
    latitude = models.DecimalField(decimal_places=7, max_digits=9)  # Range = [-90, 90]
    longitude = models.DecimalField(decimal_places=7, max_digits=10)  # Range = [-180, 180]
    
    # TODO: def get_operation_hours(self, date)
    
    @cached_property
    def rating(self):
        reviews = Review.objects.filter(restaurant=self)
        return sum([review.rating for review in reviews]) / reviews.count()

    def refresh_from_db(self, *args, **kwargs):
        super(Restaurant, self).refresh_from_db(*args, **kwargs)
        try:
            # Refresh cached property
            del self.__dict__['rating']
        except AttributeError:
            # Property has not been cached
            pass
    
    @property
    def coordinates(self):
        return (self.latitude, self.longitude)
    
    @property
    def is_open_according_to_regular_menu_hours(self):
        return self.current_menu is not None
    
    @property
    def is_on_holiday(self):
        return Holiday.objects.filter(
            restaurant=self, 
            start_datetime__lte=timezone.now(), 
            end_datetime__gte=timezone.now()
        ).exists()
    
    @property
    def is_paused(self):
        return PauseHours.objects.filter(
            restaurant=self, 
            start_datetime__lte=timezone.now(), 
            end_datetime__gte=timezone.now()
        ).exists()
    
    @property
    def is_open(self):
        return self.is_open_according_to_regular_menu_hours and not self.is_on_holiday and not self.is_paused

    # TODO: @property next_opening_datetime 
    
    @property
    def current_menu(self):
        try:
            current_time = timezone.now()
            menu_hours = MenuHours.objects.get(
                menu__restaurant=self,
                start_time__lte=current_time, 
                end_time__gt=current_time, 
                day_of_the_week=current_time.weekday()
            )
            return menu_hours.menu
        except MenuHours.DoesNotExist:
            return None

    @property
    def order_fulfillment_time(self):
        num_orders_in_progress = self.orders.filter(
            cancellation__isnull=True, 
            completed__isnull=True
        ).count()
        return timedelta(minutes=10) + (num_orders_in_progress * timedelta(minutes=3))
    
    def __str__(self):
        return self.name


class Merchant(models.Model):
    user = models.OneToOneField('delivery.User', on_delete=models.CASCADE)
    restaurant = models.OneToOneField('Restaurant', on_delete=models.CASCADE)
    
    def __str__(self):
        return f'{str(self.restaurant)} staff: {str(self.user)}'


class Menu(models.Model):
    name = models.CharField(max_length=100)
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, 
                                   related_name='menus')
    
    def __str__(self):
        return f'Menu: {self.name}'


class MenuCategory(models.Model):
    name = models.CharField(max_length=30)
    menu = models.ForeignKey('Menu', on_delete=models.CASCADE, 
                             related_name='categories')
    
    def __str__(self):
        return f'Menu Category: {self.name}'


class MenuItem(models.Model):
    name = models.CharField(max_length=30)
    price = models.DecimalField(decimal_places=2, max_digits=6)
    menu_category = models.ForeignKey('MenuCategory', on_delete=models.CASCADE, 
                                      related_name='items')
    
    def __str__(self):
        return f'Menu Item: {self.name}'


class MenuItemOptionGroup(models.Model):
    name = models.CharField(max_length=30)
    menu_item = models.ForeignKey('MenuItem', on_delete=models.CASCADE, 
                                  related_name='option_groups')
    
    MANDATORY_ONE_ONLY = 'MANDATORY_ONE_ONLY'
    MANDATORY_MULTIPLE = 'MANDATORY_MULTIPLE'
    OPTIONAL_ONE_ONLY = 'OPTIONAL_ONE_ONLY'
    OPTIONAL_MULTIPLE = 'OPTIONAL_MULTIPLE'
    OPTION_GROUP_TYPES = [
        (MANDATORY_ONE_ONLY, 'Must pick one and one only'),
        (MANDATORY_MULTIPLE, 'Must pick at least one'),
        (OPTIONAL_ONE_ONLY, 'Must pick zero or one'),
        (OPTIONAL_MULTIPLE, 'Can pick any number'),
    ]
    type = models.CharField(choices=OPTION_GROUP_TYPES, max_length=20)

    def __str__(self):
        return f'Menu Item Option Group: {self.name}'


class MenuItemOption(models.Model):
    name = models.CharField(max_length=30)
    option_group = models.ForeignKey('MenuItemOptionGroup', on_delete=models.CASCADE, 
                                     related_name='options')
    price = models.DecimalField(decimal_places=2, max_digits=6, default=0)

    def __str__(self):
        return f'Menu Item Option: {self.name}'


class OrderCancellation(models.Model):
    order = models.OneToOneField('Order', on_delete=models.CASCADE, 
                                 related_name='cancellation')
    reason = models.CharField(max_length=200, blank=True, null=True)
    

class Delivery(models.Model):
    order = models.OneToOneField('Order', on_delete=models.CASCADE, 
                                 related_name='delivery')
    session = models.ForeignKey('rider.Session', on_delete=models.CASCADE, 
                                related_name='deliveries', blank=True, null=True)
    delivery_cost = models.DecimalField(decimal_places=2, max_digits=4)
    estimated_delivery_datetime = models.DateTimeField()
    rider_pickup_datetime = models.DateTimeField(blank=True, null=True)
    
    def pick_up(self):
        self.rider_pickup_datetime = timezone.now()
        self.save()


class SelfPickup(models.Model):
    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='self_pickup')
    estimated_pickup_datetime = models.DateTimeField() 


class Order(models.Model):
    client = models.ForeignKey('client.Client', on_delete=models.CASCADE, 
                               related_name='orders')
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, 
                                   related_name='orders')

    created = models.DateTimeField(default=timezone.now)
    kitchen_completed = models.DateTimeField(blank=True, null=True)
    delay_count = models.PositiveSmallIntegerField(default=0)

    # Use `Order.completed` rather than having separate fields in `Delivery` and `SelfPickup`
    # to simplify queries for completed/in-progress orders.
    completed = models.DateTimeField(blank=True, null=True)

    DELIVERY = 'DELIVERY'
    SELF_PICKUP = 'SELF_PICKUP'
    @property
    def type(self):
        if hasattr(self, 'delivery'):
            return Order.DELIVERY
        elif hasattr(self, 'self_pickup'):
            return Order.SELF_PICKUP
        raise ValidationError(f'Order {self.id} is neither of delivery or self-pickup type')

    IN_KITCHEN = 'IN_KITCHEN'
    READY_TO_PICKUP_AT_RESTAURANT = 'READY_TO_PICKUP_AT_RESTAURANT'
    SEARCHING_FOR_RIDER = 'SEARCHING_FOR_RIDER'
    DELIVERY_IN_TRANSIT = 'DELIVERY_IN_TRANSIT'
    CANCELLED = 'CANCELLED'
    COMPLETED = 'COMPLETED'
    @property
    def status(self):   
        '''
        Delivery order: IN_KITCHEN -> READY_TO_PICKUP_AT_RESTAURANT -> DELIVERY_IN_TRANSIT -> COMPLETED
        Self-pickup order: IN_KITCHEN -> READY_TO_PICKUP_AT_RESTAURANT -> COMPLETED
        '''
        if hasattr(self, 'cancellation'): 
            return Order.CANCELLED
        
        if self.completed:
            return Order.COMPLETED
        
        if self.type == Order.DELIVERY:
            if not self.delivery.session:
                return Order.SEARCHING_FOR_RIDER
            if self.delivery.rider_pickup_datetime:
                return Order.DELIVERY_IN_TRANSIT
            elif self.kitchen_completed:
                return Order.READY_TO_PICKUP_AT_RESTAURANT
            else:
                return Order.IN_KITCHEN
        else:
            if self.kitchen_completed:
                return Order.READY_TO_PICKUP_AT_RESTAURANT
            else:
                return Order.IN_KITCHEN

    @property
    def price(self):
        return sum(item.price for item in self.items.all())
    
    def cancel(self, reason):
        if self.status == Order.CANCELLED:
            raise ValidationError('Cannot cancel order that has already been cancelled')
        elif self.status == Order.READY_TO_PICKUP_AT_RESTAURANT:
            raise ValidationError('Cannot cancel order that is ready to be picked up')
        elif self.status == Order.COMPLETED:
            raise ValidationError('Cannot cancel order that has already been completed')
        OrderCancellation.objects.create(order=self, reason=reason)

    def finish_cooking(self):
        if self.status == Order.CANCELLED:
            raise ValidationError('Cannot cancel order that has already been cancelled')
        elif self.status == Order.READY_TO_PICKUP_AT_RESTAURANT:
            raise ValidationError('Cannot cancel order that is ready to be picked up')
        elif self.status == Order.COMPLETED:
            raise ValidationError('Cannot cancel order that has already been completed')      
        self.kitchen_completed = timezone.now()
        self.save()

    @transaction.atomic
    def delay(self, delay_by):
        if self.delay_count > 2:
            raise ValidationError('Order has already been delayed twice, and cannot be delayed further')
            
        self.delay_count += 1
        self.save()
        
        if self.type == Order.DELIVERY:
            self.delivery.estimated_delivery_datetime += delay_by
            self.delivery.save()
        else:
            self.self_pickup.estimated_pickup_datetime += delay_by
            self.self_pickup.save()
    
    def complete(self):
        if self.status == Order.CANCELLED:
            raise ValidationError('Cannot complete order that has already been cancelled')
        elif self.status == Order.COMPLETED:
            raise ValidationError('Cannot complete order that has already been completed')
        
        if self.type == Order.DELIVERY and self.status != Order.DELIVERY_IN_TRANSIT:
            raise ValidationError('Invalid order state to complete delivery order')
        elif self.type == Order.SELF_PICKUP and self.status != Order.READY_TO_PICKUP_AT_RESTAURANT:
            raise ValidationError('Invalid order state to complete self-pickup order')
            
        self.completed = timezone.now()
        self.save()
        
    def __str__(self):
        return f'Order for {str(self.client)} by {str(self.restaurant)}'


class OrderItemPriceAdjustment(models.Model):
    order_item = models.OneToOneField('OrderItem', on_delete=models.PROTECT,
                                   related_name='price_adjustment')
    adjustment = models.DecimalField(decimal_places=2, max_digits=6, default=0)
    reason = models.CharField(max_length=50)


class OrderItem(models.Model):
    menu_item = models.ForeignKey('MenuItem', on_delete=models.PROTECT, 
                                  related_name='items')
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='items')
    quantity = models.IntegerField(default=1)

    @property
    def price(self):
        '''
        Price inclusive of options and price adjustments
        '''
        result = self.menu_item.price
        for option_group in self.option_groups.all():
            for option in option_group.options.all():
                result += option.menu_item_option.price
        if hasattr(self, 'price_adjustment'):
            result += self.price_adjustment.adjustment
        return result
    
    def __str__(self):
        return f'Order Item: {str(self.menu_item)}'


class OrderItemOptionGroup(models.Model):
    menu_item_option_group = models.ForeignKey('MenuItemOptionGroup', 
                                               on_delete=models.PROTECT, 
                                               related_name='order_item_option_groups')
    order_item = models.ForeignKey('OrderItem', on_delete=models.CASCADE, 
                                   related_name='option_groups')
    
    def __str__(self):
        return f'Order Item Option Group: {str(self.menu_item_option_group)}'


class OrderItemOption(models.Model):
    menu_item_option = models.ForeignKey('MenuItemOption', 
                                         on_delete=models.PROTECT, 
                                         related_name='order_item_options')
    order_item_option_group = models.ForeignKey('OrderItemOptionGroup', 
                                                on_delete=models.CASCADE, 
                                                related_name='options')
    
    def __str__(self):
        return f'Order Item Option: {str(self.menu_item_option)}'
