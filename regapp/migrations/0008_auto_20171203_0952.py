# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-03 09:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regapp', '0007_auto_20171127_0847'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='username',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]