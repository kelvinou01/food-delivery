# Generated by Django 4.0.2 on 2022-07-19 17:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('merchant', '0008_alter_menuhours_day_of_the_week_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='menu',
            name='is_used',
        ),
        migrations.RemoveField(
            model_name='menuitem',
            name='menu',
        ),
        migrations.RemoveField(
            model_name='order',
            name='rider',
        ),
        migrations.AddField(
            model_name='menuitemoptiongroup',
            name='menu_item',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='merchant.menuitem'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='restaurant',
            name='is_live',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='restaurantstaff',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='OpeningHours',
        ),
    ]
