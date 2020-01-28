# Generated by Django 2.2.9 on 2020-01-24 13:16

import api.models
from django.db import migrations, models
import enumfields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0040_auto_20200121_1609'),
    ]

    operations = [
        migrations.CreateModel(
            name='CronJob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=100)),
                ('status', enumfields.fields.EnumIntegerField(default=-1, enum=api.models.CronJobStatus)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('message', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Cronjob log record',
                'verbose_name_plural': 'Cronjob log records',
            },
        ),
    ]
