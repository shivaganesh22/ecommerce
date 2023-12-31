# Generated by Django 4.2.4 on 2023-08-25 12:35

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_alter_order_ecommerce_id_alter_order_order_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='date',
            new_name='delivery_date',
        ),
        migrations.AddField(
            model_name='order',
            name='order_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='ecommerce_id',
            field=models.CharField(default=uuid.UUID('ef1f37a9-c239-4006-ab6b-92df8bf3312d'), max_length=100),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.BooleanField(blank=True, default=True),
        ),
    ]
