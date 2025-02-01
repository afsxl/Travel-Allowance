# Generated by Django 4.2.18 on 2025-02-01 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ta', '0004_remove_routestop_isinstitute_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='routestop',
            name='stopType',
            field=models.CharField(choices=[('1', 'Intermediate Stop'), ('2', 'Institute'), ('3', 'Valuation Camp')], max_length=100),
        ),
    ]
