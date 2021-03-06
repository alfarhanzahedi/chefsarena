# Generated by Django 2.1 on 2018-09-22 12:29

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_customset_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='customset',
            name='duration',
            field=models.BigIntegerField(default=10800),
        ),
        migrations.AddField(
            model_name='customset',
            name='unique_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
