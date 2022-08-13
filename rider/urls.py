from django.contrib import admin
from django.urls import include, path

from rider.views import OrderAccept, OrderCancel, OrderComplete, OrderDetail, OrderList, \
    OrderPickup, CurrentSessionEnd, CurrentSessionExtend, RiderRegister, SessionListCreate, SessionOrderList, CurrentSessionOrderList


app_name = 'Rider'


urlpatterns = [
    path('register/', RiderRegister.as_view(), name='register'),
    path('sessions/', SessionListCreate.as_view(), name='sessions'),
    path('sessions/current/end/', CurrentSessionEnd.as_view(), name='current_session_end'),
    path('sessions/current/extend/', CurrentSessionExtend.as_view(), name='current_session_extend'),
    path('sessions/current/orders/', CurrentSessionOrderList.as_view(), name='current_session_orders_list'),
    path('sessions/<session_id>/orders/', SessionOrderList.as_view(), name='session_orders_list'),
    path('orders/', OrderList.as_view(), name='orders'),
    path('orders/<order_id>/', OrderDetail.as_view(), name='order_detail'),
    path('orders/<order_id>/accept/', OrderAccept.as_view(), name='order_accept'), 
    path('orders/<order_id>/pickup/', OrderPickup.as_view(), name='order_pickup'),
    path('orders/<order_id>/complete/', OrderComplete.as_view(), name='order_complete'),
    path('orders/<order_id>/cancel/', OrderCancel.as_view(), name='order_cancel'),
]
