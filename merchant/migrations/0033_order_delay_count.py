# Generated by Django 4.0.6 on 2022-08-10 02:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchant', '0032_delivery_delivery_cost'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delay_count',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
