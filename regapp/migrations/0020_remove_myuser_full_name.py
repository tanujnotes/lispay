# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-13 06:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('regapp', '0019_auto_20180329_1313'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myuser',
            name='full_name',
        ),
    ]
