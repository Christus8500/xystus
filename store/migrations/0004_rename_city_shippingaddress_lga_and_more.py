# Generated by Django 4.2.7 on 2024-01-30 19:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_alter_product_original_price'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shippingaddress',
            old_name='city',
            new_name='lga',
        ),
        migrations.RenameField(
            model_name='shippingaddress',
            old_name='zipcode',
            new_name='town',
        ),
    ]
