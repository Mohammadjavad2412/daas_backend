# Generated by Django 4.2.4 on 2023-09-03 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_daas'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='daas',
            name='port',
        ),
        migrations.AddField(
            model_name='daas',
            name='http_port',
            field=models.PositiveIntegerField(null=True, unique=True),
        ),
        migrations.AddField(
            model_name='daas',
            name='https_port',
            field=models.PositiveIntegerField(null=True, unique=True),
        ),
    ]
