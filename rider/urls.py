from django.contrib import admin
from django.urls import include, path

from rider.views import OrderAccept, OrderCancel, OrderComplete, OrderDetail, OrderList, \
    OrderPickup, SessionEnd, SessionExtend, SessionListCreate, SessionOrdersList


app_name = 'Rider'


urlpatterns = [
    # path('register/'),
    # path('login/'), 
    path('sessions/', SessionListCreate.as_view(), name='sessions'),
    path('sessions/<session_id>/end/', SessionEnd.as_view(), name='session_end'),
    path('sessions/<session_id>/extend/', SessionExtend.as_view(), name='session_extend'),
    path('sessions/<session_id>/orders/', SessionOrdersList.as_view(), name='session_orders_list'),
    path('orders/', OrderList.as_view(), name='orders'),
    path('orders/<order_id>/', OrderDetail.as_view(), name='order_detail'),
    path('orders/<order_id>/accept/', OrderAccept.as_view(), name='order_accept'), 
    path('orders/<order_id>/pickup/', OrderPickup.as_view(), name='order_pickup'),
    path('orders/<order_id>/complete/', OrderComplete.as_view(), name='order_complete'),
    path('orders/<order_id>/cancel/', OrderCancel.as_view(), name='order_cancel'),
]
