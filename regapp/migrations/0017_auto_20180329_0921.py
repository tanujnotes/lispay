# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-29 09:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regapp', '0016_myuser_last_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='featured_video',
            field=models.URLField(),
        ),
    ]