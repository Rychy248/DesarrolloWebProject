# Generated by Django 3.2.7 on 2021-09-19 23:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='account',
            options={'verbose_name': 'Account', 'verbose_name_plural': 'Accounts'},
        ),
    ]
