# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-11 17:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regapp', '0014_subscriptionmodel_start_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
