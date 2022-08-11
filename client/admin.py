from django.contrib import admin
from client.models import Client, Review, Voucher


admin.site.register(Client)
admin.site.register(Voucher)
admin.site.register(Review)
