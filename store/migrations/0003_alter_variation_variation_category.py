# Generated by Django 3.2.7 on 2021-10-05 22:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_variation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variation',
            name='variation_category',
            field=models.CharField(choices=[('color', 'color'), ('talla', 'talla')], max_length=100),
        ),
    ]
