# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-29 10:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regapp', '0017_auto_20180329_0921'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='username',
            field=models.CharField(error_messages={'unique': 'A user with this username already exists.'}, max_length=30, unique=True),
        ),
    ]
