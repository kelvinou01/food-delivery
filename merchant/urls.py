
from django.urls import path

from merchant.views import HolidayDetail, MenuDetail, MenuHoursListCreate, MenuItemDetail, MenuItemsListCreate, MenuListCreate, MerchantRegister, OrderCancel, OrderDelay, OrderFinishCooking, OrderList, OrderDetail, PriceAdjustment, RestaurantCreate, Status, HolidayListCreate

app_name = 'Merchant'

urlpatterns = [
    path('restaurants/', RestaurantCreate.as_view(), name='restaurants'),
    path('restaurants/<int:restaurant_id>/menu-hours/', MenuHoursListCreate.as_view(), name='restuarants'),
    path('restaurants/<int:restaurant_id>/status/', Status.as_view(), name='status'),
    path('restaurants/<int:restaurant_id>/holidays/', HolidayListCreate.as_view(), name='holidays'),
    path('restaurants/<int:restaurant_id>/holidays/<int:holiday_id>/', HolidayDetail.as_view(), name='holidays_detail'),
    path('restaurants/<int:restaurant_id>/menus/', MenuListCreate.as_view(), name='menus'),
    path('restaurants/<int:restaurant_id>/menus/<int:menu_id>/', MenuDetail.as_view(), name='menu_detail'),
    path('restaurants/<int:restaurant_id>/menus/<int:menu_id>/items/', MenuItemsListCreate.as_view(), name='menu_items'), 
    path('restaurants/<int:restaurant_id>/menus/<int:menu_id>/items/<int:item_id>/', MenuItemDetail.as_view(), name='menu_item_detail'),
    path('restaurants/<int:restaurant_id>/orders/', OrderList.as_view(), name='orders_list'),
    path('restaurants/<int:restaurant_id>/orders/<int:order_id>/', OrderDetail.as_view(), name='order_detail'),    
    path('restaurants/<int:restaurant_id>/orders/<int:order_id>/finish-cooking/', OrderFinishCooking.as_view(), name='order_finish_cooking'),
    path('restaurants/<int:restaurant_id>/orders/<int:order_id>/cancel/', OrderCancel.as_view(), name='order_cancel'),
    path('restaurants/<int:restaurant_id>/orders/<int:order_id>/delay/', OrderDelay.as_view(), name='order_delay'),
    path('restaurants/<int:restaurant_id>/orders/<int:order_id>/items/<int:order_item_id>/adjust-price/', PriceAdjustment.as_view(), name='order_item_price_adjustment'),
]
