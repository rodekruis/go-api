# Generated by Django 2.2.10 on 2020-04-06 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0050_auto_20200406_0614'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldreport',
            name='sit_fields_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
