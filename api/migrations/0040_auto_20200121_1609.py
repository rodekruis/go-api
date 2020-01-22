# Generated by Django 2.2.9 on 2020-01-21 16:09

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0039_auto_20200110_1546'),
    ]

    operations = [
        migrations.AlterField(
            model_name='action',
            name='field_report_types',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('EVT', 'Event'), ('EW', 'Early Warning')], max_length=4), default=list, size=None),
        ),
    ]