# Generated by Django 2.1 on 2018-09-30 09:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20180929_1745'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='codechefcookoff',
            options={'ordering': ['-code']},
        ),
    ]