from django.contrib import admin

from merchant.models import Delivery, Holiday, Menu, MenuCategory, MenuHours, MenuItem, MenuItemOption, MenuItemOptionGroup, Order, OrderItem, OrderItemOption, OrderItemOptionGroup, PauseHours, Restaurant, Merchant, SelfPickup


admin.site.register(MenuHours)
admin.site.register(Restaurant)
admin.site.register(Merchant)
admin.site.register(Menu)
admin.site.register(MenuCategory)
admin.site.register(MenuItem)
admin.site.register(MenuItemOptionGroup)
admin.site.register(MenuItemOption)
admin.site.register(Order)
admin.site.register(Delivery)
admin.site.register(SelfPickup)
admin.site.register(OrderItem)
admin.site.register(OrderItemOptionGroup)
admin.site.register(OrderItemOption)
admin.site.register(Holiday)
admin.site.register(PauseHours)
