# Generated by Django 2.2.9 on 2022-01-19 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0014_auto_20211207_1042'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='total_price',
            field=models.IntegerField(default=0),
        ),
    ]