# Generated by Django 5.0 on 2024-02-23 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0010_claim_claim_period'),
    ]

    operations = [
        migrations.AddField(
            model_name='budget',
            name='budget_notes',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
