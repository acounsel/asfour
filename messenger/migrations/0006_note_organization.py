# Generated by Django 3.0.4 on 2020-04-05 00:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0005_auto_20200404_1616'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='organization',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='messenger.Organization'),
            preserve_default=False,
        ),
    ]
