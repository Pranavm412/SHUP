# Generated by Django 5.1.5 on 2025-03-05 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_account_address_line_1'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='pincode',
        ),
        migrations.AlterField(
            model_name='account',
            name='address_line_1',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='account',
            name='address_line_2',
            field=models.CharField(max_length=50),
        ),
    ]
