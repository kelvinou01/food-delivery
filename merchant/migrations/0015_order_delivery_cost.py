# Generated by Django 4.0.6 on 2022-07-22 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchant', '0014_menuitemoption_price_orderitem_quantity_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_cost',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True),
        ),
    ]
