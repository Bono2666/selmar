# Generated by Django 5.0 on 2024-01-06 17:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0002_rename_claim_proposal_claim_amt_claim'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proposal',
            name='claim_amt',
        ),
    ]
