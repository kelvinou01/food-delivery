# Generated by Django 4.0.6 on 2022-07-23 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchant', '0016_alter_order_session_pausehours_holidayhours'),
    ]

    operations = [
        migrations.AddField(
            model_name='pausehours',
            name='reason',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
