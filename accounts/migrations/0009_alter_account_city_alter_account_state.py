# Generated by Django 5.1.5 on 2025-03-05 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_alter_account_city_alter_account_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='city',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='state',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
