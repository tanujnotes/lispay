# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-08 08:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regapp', '0003_auto_20170608_0711'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='is_creator',
            field=models.BooleanField(default=False),
        ),
    ]