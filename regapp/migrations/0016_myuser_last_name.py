# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-11 17:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regapp', '0015_myuser_first_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='last_name',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]