# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-13 07:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regapp', '0009_auto_20171211_1037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='short_bio',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
