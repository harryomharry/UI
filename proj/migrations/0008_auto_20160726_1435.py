# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-26 18:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proj', '0007_auto_20160726_1433'),
    ]

    operations = [
        migrations.RenameField(
            model_name='current',
            old_name='clientnnum',
            new_name='clientnum',
        ),
    ]
