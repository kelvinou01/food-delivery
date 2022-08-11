from rest_framework import permissions
from django.core.exceptions import ObjectDoesNotExist

from merchant.models import Order, OrderItem, Restaurant


class IsRestaurantStaff(permissions.BasePermission):
    '''
    Checks if the user is a restaurant staff of the restaurant_id given in the url parameter
    '''
    def has_permission(self, request, view):
        try: 
            return request.user.restaurantstaff.restaurant.id == view.kwargs['restaurant_id']
        except ObjectDoesNotExist:
            return False


class OrderIsForRestaurant(permissions.BasePermission):
    '''
    Checks if the restaurant is the recipient of the order_id given in the url parameter
    '''
    def has_permission(self, request, view):
        try: 
            order_from_kwarg = Order.objects.get(id=view.kwargs['order_id'])
            restaurant_from_kwarg = Restaurant.objects.get(id=view.kwargs['restaurant_id'])
            return order_from_kwarg.restaurant == restaurant_from_kwarg
        except ObjectDoesNotExist:
            return False


class OrderItemIsInOrder(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            order_from_kwarg = Order.objects.get(id=view.kwargs['order_id'])
            order_item_from_kwarg = OrderItem.objects.get(id=view.kwargs['order_item_id'])
            return order_item_from_kwarg.order == order_from_kwarg
        except ObjectDoesNotExist:
            return False 