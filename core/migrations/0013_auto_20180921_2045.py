# Generated by Django 2.1 on 2018-09-21 20:45

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20180917_1854'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32)),
                ('description', models.CharField(max_length=256)),
                ('problems', models.ManyToManyField(to='core.Problem')),
            ],
        ),
        migrations.AlterField(
            model_name='submission',
            name='time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]