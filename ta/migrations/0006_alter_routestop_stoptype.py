# Generated by Django 4.2.18 on 2025-02-01 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ta', '0005_alter_routestop_stoptype'),
    ]

    operations = [
        migrations.AlterField(
            model_name='routestop',
            name='stopType',
            field=models.IntegerField(choices=[('1', 'Intermediate Stop'), ('2', 'Institute'), ('3', 'Valuation Camp')]),
        ),
    ]
