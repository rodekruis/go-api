# Generated by Django 2.2.13 on 2020-06-12 04:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deployments', '0029_merge_20200610_1014'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='name_ar',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='name_en',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='name_es',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='name_fr',
            field=models.TextField(null=True),
        ),
    ]
