# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-11-18 12:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regapp', '0004_auto_20171118_1117'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentmodel',
            name='fee',
            field=models.DecimalField(decimal_places=2, default='0.0', max_digits=9),
        ),
        migrations.AlterField(
            model_name='subscriptionmodel',
            name='paid_count',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]