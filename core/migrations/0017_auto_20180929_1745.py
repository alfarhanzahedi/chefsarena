# Generated by Django 2.1 on 2018-09-29 17:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20180929_1745'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customset',
            options={'ordering': ['-updated_at']},
        ),
    ]
