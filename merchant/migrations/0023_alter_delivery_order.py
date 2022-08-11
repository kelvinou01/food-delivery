# Generated by Django 4.0.6 on 2022-08-05 06:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('merchant', '0022_remove_order_delivery_cost_remove_order_session_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delivery',
            name='order',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='deliveries', to='merchant.order'),
        ),
    ]
