# Generated by Django 4.0.2 on 2022-07-25 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchant', '0019_remove_order_status_order_completed_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitemoptiongroup',
            name='type',
            field=models.CharField(choices=[('MANDATORY_ONE_ONLY', 'Must pick one and one only'), ('MANDATORY_MULTIPLE', 'Must pick at least one'), ('OPTIONAL_ONE_ONLY', 'Must pick zero or one'), ('OPTIONAL_MULTIPLE', 'Can pick any number')], max_length=20),
        ),
        migrations.AlterField(
            model_name='order',
            name='type',
            field=models.CharField(choices=[('DELIVERY', 'Delivery'), ('SELF_PICKUP', 'Self pickup')], max_length=20),
        ),
    ]
