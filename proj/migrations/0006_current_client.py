# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-26 17:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proj', '0005_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='current',
            name='client',
            field=models.CharField(default=0, max_length=200),
            preserve_default=False,
        ),
    ]
