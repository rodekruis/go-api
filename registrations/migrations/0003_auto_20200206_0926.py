# Generated by Django 2.2.9 on 2020-02-06 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0002_auto_20180626_1808'),
    ]

    operations = [
        migrations.AddField(
            model_name='pending',
            name='admin_1_validated_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pending',
            name='admin_2_validated_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
