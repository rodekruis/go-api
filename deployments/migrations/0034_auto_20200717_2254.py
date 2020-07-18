# Generated by Django 2.2.13 on 2020-07-17 22:54

import deployments.models
from django.db import migrations
import enumfields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('deployments', '0033_auto_20200716_2301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='activity',
            field=enumfields.fields.EnumIntegerField(default=0, enum=deployments.models.Activities, verbose_name='activity'),
        ),
        migrations.AlterField(
            model_name='project',
            name='beneficiary_type',
            field=enumfields.fields.EnumIntegerField(default=0, enum=deployments.models.BeneficiaryTypes, verbose_name='beneficiary type'),
        ),
        migrations.AlterField(
            model_name='project',
            name='subactivity',
            field=enumfields.fields.EnumIntegerField(default=0, enum=deployments.models.Subactivities, verbose_name='subactivity'),
        ),
        migrations.AlterField(
            model_name='project',
            name='units_measurement_metric',
            field=enumfields.fields.EnumIntegerField(default=0, enum=deployments.models.UnitsMeasurementMetric, verbose_name='units measurement metric'),
        ),
        migrations.AlterField(
            model_name='project',
            name='where_delivery_service_place',
            field=enumfields.fields.EnumIntegerField(default=0, enum=deployments.models.DeliveryServicePlaces, verbose_name='where delivery service place'),
        ),
        migrations.AlterField(
            model_name='project',
            name='where_district',
            field=enumfields.fields.EnumIntegerField(default=0, enum=deployments.models.Districts, verbose_name='where district'),
        ),
        migrations.AlterField(
            model_name='project',
            name='where_municipality',
            field=enumfields.fields.EnumIntegerField(default=0, enum=deployments.models.Municipalities, verbose_name='where municipality'),
        ),
        migrations.AlterField(
            model_name='project',
            name='where_province',
            field=enumfields.fields.EnumIntegerField(default=0, enum=deployments.models.Provinces, verbose_name='where province'),
        ),
    ]