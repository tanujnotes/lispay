# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-25 10:31
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('regapp', '0023_datadumpmodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransactionModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_id', models.CharField(max_length=255)),
                ('transaction_type', models.CharField(max_length=255)),
                ('transaction_status', models.CharField(choices=[('waiting', 'Waiting for confirmation'), ('preauth', 'Pre-authorized'), ('confirmed', 'Confirmed'), ('rejected', 'Rejected'), ('refunded', 'Refunded'), ('error', 'Error'), ('input', 'Input')], default='waiting', max_length=20)),
                ('tax', models.DecimalField(decimal_places=2, default='0.0', max_digits=9)),
                ('captured_amount', models.DecimalField(decimal_places=2, default='0.0', max_digits=9)),
                ('total_amount', models.DecimalField(decimal_places=2, default='0.0', max_digits=9)),
                ('currency', models.CharField(max_length=10)),
                ('message', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('creator', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, related_name='creator_transaction', to=settings.AUTH_USER_MODEL)),
                ('subscriber', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, related_name='subscriber_transaction', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]