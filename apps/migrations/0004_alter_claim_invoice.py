# Generated by Django 5.0.6 on 2024-06-29 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0003_alter_claim_invoice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='claim',
            name='invoice',
            field=models.CharField(max_length=50, null=True),
        ),
    ]