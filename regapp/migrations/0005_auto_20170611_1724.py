# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-11 17:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regapp', '0004_myuser_is_creator'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myuser',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='myuser',
            name='last_name',
        ),
        migrations.AddField(
            model_name='myuser',
            name='full_name',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]