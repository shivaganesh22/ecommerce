# Generated by Django 4.2.4 on 2023-08-25 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_rename_date_order_delivery_date_order_order_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='ecommerce_id',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
