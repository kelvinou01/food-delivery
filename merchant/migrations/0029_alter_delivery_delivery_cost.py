# Generated by Django 4.0.6 on 2022-08-09 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchant', '0028_alter_delivery_delivery_cost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delivery',
            name='delivery_cost',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
