# Generated by Django 5.1.5 on 2025-03-10 19:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0019_delete_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='is_verified',
        ),
        migrations.RemoveField(
            model_name='account',
            name='otp',
        ),
    ]
