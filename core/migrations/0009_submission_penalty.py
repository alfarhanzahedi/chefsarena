# Generated by Django 2.1 on 2018-09-17 05:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20180916_1931'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='penalty',
            field=models.IntegerField(default=0),
        ),
    ]