
from django.urls import path
from client.views import DeliveryOrderCreate, OrderCancel, OrderComplete, OrderDetail, OrderList, ReviewCreate, ReviewList, SelfPickupOrderCreate, RestaurantDetail, RestaurantList, MenuItemDetail



app_name = 'Client'

urlpatterns = [
    # path('register/'),
    # path('login/'),
    path('restaurants/', RestaurantList.as_view(), name='restaurants_list'), 
    path('restaurants/<int:restaurant_id>/', RestaurantDetail.as_view(), name='restaurant_detail'),
    path('restaurants/<int:restaurant_id>/items/<int:menu_item_id>/', MenuItemDetail.as_view(), name='menu_item_detail'),
    path('restaurants/<int:restaurant_id>/reviews/', ReviewList.as_view(), name='restaurant_reviews'),
    path('orders/', OrderList.as_view(), name='orders_list_create'),
    path('orders/delivery/', DeliveryOrderCreate.as_view(), name='delivery_order_create'),
    path('orders/self-pickup/', SelfPickupOrderCreate.as_view(), name='pickup_order_create'),
    path('orders/<int:order_id>/', OrderDetail.as_view(), name='order_detail'),
    path('orders/<int:order_id>/cancel/', OrderCancel.as_view(), name='order_cancel'),
    path('orders/<int:order_id>/confirm-received/', OrderComplete.as_view(), name='order_complete'),
    path('orders/<int:order_id>/review/', ReviewCreate.as_view(), name='review_create')
]
