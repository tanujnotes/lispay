# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-15 11:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('regapp', '0016_auto_20170731_1956'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subscriptionmodel',
            old_name='subs_from',
            new_name='creator',
        ),
        migrations.RenameField(
            model_name='subscriptionmodel',
            old_name='subs_to',
            new_name='subscriber',
        ),
    ]
