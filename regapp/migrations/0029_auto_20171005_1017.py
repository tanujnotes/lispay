# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-05 10:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regapp', '0028_auto_20171005_0956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='featured_text',
            field=models.CharField(blank=True, max_length=1000),
        ),
    ]
