# Generated by Django 2.2.10 on 2020-04-09 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deployments', '0021_projectimport'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='is_private',
        ),
        migrations.AddField(
            model_name='project',
            name='visibility',
            field=models.CharField(choices=[('public', 'Public'), ('logged_in_user', 'Logged in user'), ('ifrc_only', 'IFRC only')], default='public', max_length=32),
        ),
    ]
