# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-26 19:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20180123_1626'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appealdocument',
            name='created_at',
            field=models.DateTimeField(),
        ),
    ]
