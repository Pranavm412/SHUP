# Generated by Django 5.1.5 on 2025-03-05 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_remove_account_pincode_alter_account_address_line_1_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='city',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='account',
            name='state',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
