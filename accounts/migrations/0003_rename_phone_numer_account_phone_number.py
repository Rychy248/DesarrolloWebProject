# Generated by Django 3.2.7 on 2021-10-06 02:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_account_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='phone_numer',
            new_name='phone_number',
        ),
    ]
