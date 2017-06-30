# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-30 09:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regapp', '0010_auto_20170622_0943'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='myuser',
            name='thumbnail',
            field=models.ImageField(default='profile_images/profile_b.jpg', upload_to='profile_images'),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='category',
            field=models.CharField(choices=[('OTHERS', 'Others'), ('VIDEOS AND FILMS', 'Videos and Films'), ('MUSIC', 'Music'), ('WRITING', 'Writing'), ('ARTS AND CRAFTS', 'Arts and Crafts'), ('GAMES', 'Games'), ('MEDIA', 'Media'), ('PHOTOGRAPHY', 'Photography'), ('SCIENCE AND TECHNOLOGY', 'Science and Technology'), ('EDUCATION', 'Education'), ('DANCE AND THEATER', 'Dance and Theater'), ('CODING', 'Coding')], default='Coding', max_length=30),
        ),
    ]
