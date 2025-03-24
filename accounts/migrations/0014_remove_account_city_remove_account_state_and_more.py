# Generated by Django 5.1.5 on 2025-03-06 03:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_alter_account_address_line_1'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='city',
        ),
        migrations.RemoveField(
            model_name='account',
            name='state',
        ),
        migrations.AlterField(
            model_name='account',
            name='address_line_1',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='address_line_2',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
