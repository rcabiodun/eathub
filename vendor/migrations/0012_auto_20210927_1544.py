# Generated by Django 2.2.9 on 2021-09-27 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0011_auto_20210927_1500'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_location',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='delivery_location',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]