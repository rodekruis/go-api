# Generated by Django 2.0.8 on 2018-10-16 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20181015_0934'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='hide_attached_field_reports',
            field=models.BooleanField(default=False),
        ),
    ]