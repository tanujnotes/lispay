# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-05 11:24
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regapp', '0029_auto_20171005_1017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subsplanmodel',
            name='amount',
            field=models.SmallIntegerField(),
        ),
        migrations.AlterField(
            model_name='subsplanmodel',
            name='description',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='subsplanmodel',
            name='interval',
            field=models.SmallIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='subsplanmodel',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='subsplanmodel',
            name='notes',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='subsplanmodel',
            name='period',
            field=models.CharField(default='monthly', max_length=20),
        ),
        migrations.AlterField(
            model_name='subsplanmodel',
            name='plan_id',
            field=models.CharField(max_length=255),
        ),
    ]
