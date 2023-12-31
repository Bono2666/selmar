# Generated by Django 5.0 on 2024-01-06 17:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='proposal',
            old_name='claim',
            new_name='claim_amt',
        ),
        migrations.CreateModel(
            name='Claim',
            fields=[
                ('claim_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('claim_date', models.DateTimeField(null=True)),
                ('invoice', models.CharField(max_length=50, null=True)),
                ('invoice_date', models.DateTimeField(null=True)),
                ('due_date', models.DateTimeField(null=True)),
                ('amount', models.DecimalField(decimal_places=0, default=0, max_digits=12)),
                ('tax', models.DecimalField(decimal_places=0, default=0, max_digits=12)),
                ('remarks', models.TextField(null=True)),
                ('entry_date', models.DateTimeField(null=True)),
                ('entry_by', models.CharField(max_length=50, null=True)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('update_by', models.CharField(blank=True, max_length=50, null=True)),
                ('area', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='apps.areasales')),
                ('program', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='apps.program')),
                ('proposal', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='apps.proposal')),
            ],
        ),
    ]
