# Generated by Django 3.0.4 on 2020-04-13 03:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0013_auto_20200412_1425'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='request_for_response',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='response',
            name='recording',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='response',
            name='sid',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
