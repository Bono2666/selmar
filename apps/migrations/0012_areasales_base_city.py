# Generated by Django 5.0 on 2024-02-24 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0011_budget_budget_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='areasales',
            name='base_city',
            field=models.CharField(max_length=50, null=True),
        ),
    ]