# Generated by Django 3.1.7 on 2021-07-07 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0023_auto_20210615_0956'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ('-date_sent', '-date_created')},
        ),
        migrations.AddField(
            model_name='messagelog',
            name='sid',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
