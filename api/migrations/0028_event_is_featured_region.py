# Generated by Django 2.0.12 on 2019-11-27 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0027_auto_20191120_1223'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='is_featured_region',
            field=models.BooleanField(default=False),
        ),
    ]
