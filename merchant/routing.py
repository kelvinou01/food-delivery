from django.urls import path, re_path

from merchant.consumers import OrderConsumer

websocket_urlpatterns = [
    re_path(
        r'merchant/restaurants/(?P<restaurant_id>\d+)/orders/', 
        OrderConsumer.as_asgi(), 
        name='order_list_ws'
    ),
]
