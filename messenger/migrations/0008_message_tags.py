# Generated by Django 3.0.4 on 2020-04-07 05:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0007_auto_20200406_2139'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='tags',
            field=models.ManyToManyField(blank=True, to='messenger.Tag'),
        ),
    ]