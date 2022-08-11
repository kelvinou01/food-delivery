from rest_framework import permissions
from django.core.exceptions import ObjectDoesNotExist

from merchant.models import Order
from rider.models import Session


class IsRider(permissions.BasePermission):
    '''
    Checks if the user is a rider
    '''
    def has_permission(self, request, view):
        try: 
            request.user.rider
            return True
        except ObjectDoesNotExist:
            return False

class IsDeliveringThisOrder(permissions.BasePermission):
    '''
    Checks if the rider is delivering the order specified in the url kwarg
    '''
    def has_permission(self, request, view):
        try: 
            order = Order.objects.get(id=view.kwargs.get('order_id'))
            return request.user.rider.current_session == order.delivery.session
        except ObjectDoesNotExist:
            return False

class RiderOwnsSession(permissions.BasePermission):
    '''
    Checks if the rider owns the session specified in the url kwarg
    '''
    def has_permission(self, request, view):
        try: 
            session = Session.objects.get(id=view.kwargs.get('session_id'))
            return request.user.rider == session.rider
        except ObjectDoesNotExist:
            return False
