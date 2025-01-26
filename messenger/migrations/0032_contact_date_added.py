# Generated by Django 4.2.5 on 2025-01-21 19:51

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0031_tag_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
