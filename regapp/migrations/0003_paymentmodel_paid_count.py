# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-11-18 05:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regapp', '0002_auto_20171117_1754'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentmodel',
            name='paid_count',
            field=models.PositiveSmallIntegerField(blank=True, default=0),
            preserve_default=False,
        ),
    ]
