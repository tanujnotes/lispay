# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-05 12:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regapp', '0031_auto_20171005_1126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriptionmodel',
            name='status',
            field=models.CharField(choices=[('unknown', 'unknown'), ('created', 'created'), ('authenticated', 'authenticated'), ('active', 'active'), ('pending', 'pending'), ('halted', 'halted'), ('cancelled', 'cancelled'), ('completed', 'completed'), ('expired', 'expired')], default='unknown', max_length=30),
        ),
    ]
