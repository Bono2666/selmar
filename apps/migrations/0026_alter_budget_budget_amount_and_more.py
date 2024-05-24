# Generated by Django 5.0 on 2024-05-15 01:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0025_alter_incrementalsales_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budget',
            name='budget_amount',
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
        migrations.AlterField(
            model_name='budget',
            name='budget_balance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AlterField(
            model_name='budget',
            name='budget_total',
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
        migrations.AlterField(
            model_name='budget',
            name='budget_upping',
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
    ]