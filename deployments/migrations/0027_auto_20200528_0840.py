# Generated by Django 2.2.10 on 2020-05-28 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deployments', '0026_sector_health_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_districts',
            field=models.ManyToManyField(to='api.District'),
        ),
    ]
