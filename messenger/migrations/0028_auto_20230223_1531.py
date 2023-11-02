# Generated by Django 3.2.18 on 2023-02-23 23:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0027_auto_20211008_1155'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='is_international',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='message',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='messenger.userprofile'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='phone',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='message',
            name='method',
            field=models.CharField(choices=[('sms', 'SMS'), ('voice', 'Voice'), ('email', 'Email'), ('whatsapp', 'WhatsApp'), ('conference', 'Conference Call'), ('mixed', 'Mixed')], default='sms', max_length=50),
        ),
    ]