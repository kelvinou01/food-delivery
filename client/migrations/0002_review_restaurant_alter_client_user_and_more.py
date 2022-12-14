# Generated by Django 4.0.2 on 2022-07-20 05:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('merchant', '0009_remove_menu_is_used_remove_menuitem_menu_and_more'),
        ('client', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='restaurant',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='merchant.restaurant'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='client',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='review',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='client.client'),
        ),
    ]
