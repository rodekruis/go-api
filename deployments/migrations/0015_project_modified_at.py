# Generated by Django 2.0.12 on 2019-10-10 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deployments', '0014_auto_20191004_0646'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='modified_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]