# Generated by Django 5.0 on 2024-02-15 10:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0005_alter_proposalattachment_attachment'),
    ]

    operations = [
        migrations.CreateModel(
            name='BudgetTransfer',
            fields=[
                ('transfer_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('date', models.DateTimeField(null=True)),
                ('amount', models.DecimalField(decimal_places=0, default=0, max_digits=12)),
                ('status', models.CharField(default='PENDING', max_length=15)),
                ('entry_date', models.DateTimeField(null=True)),
                ('entry_by', models.CharField(max_length=50, null=True)),
                ('update_date', models.DateTimeField(null=True)),
                ('update_by', models.CharField(max_length=50, null=True)),
                ('area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apps.areasales')),
                ('channel_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='channel_from', to='apps.channel')),
                ('channel_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='channel_to', to='apps.channel')),
                ('distributor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apps.distributor')),
            ],
        ),
        migrations.CreateModel(
            name='BudgetTransferMatrix',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence', models.IntegerField(default=0)),
                ('entry_date', models.DateTimeField(null=True)),
                ('entry_by', models.CharField(max_length=50, null=True)),
                ('update_date', models.DateTimeField(null=True)),
                ('update_by', models.CharField(max_length=50, null=True)),
                ('approver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apps.areasales')),
                ('position', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='apps.position')),
            ],
        ),
        migrations.CreateModel(
            name='BudgetTransferRelease',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transfer_approval_id', models.CharField(max_length=50, null=True)),
                ('transfer_approval_name', models.CharField(max_length=50, null=True)),
                ('transfer_approval_email', models.CharField(max_length=50, null=True)),
                ('transfer_approval_position', models.CharField(max_length=50, null=True)),
                ('transfer_approval_date', models.DateTimeField(null=True)),
                ('transfer_approval_status', models.CharField(default='N', max_length=1)),
                ('update_note', models.CharField(max_length=200, null=True)),
                ('return_note', models.CharField(max_length=200, null=True)),
                ('sequence', models.IntegerField(default=0)),
                ('entry_date', models.DateTimeField(null=True)),
                ('entry_by', models.CharField(max_length=50, null=True)),
                ('update_date', models.DateTimeField(null=True)),
                ('update_by', models.CharField(max_length=50, null=True)),
                ('transfer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apps.budgettransfer')),
            ],
        ),
        migrations.AddConstraint(
            model_name='budgettransfermatrix',
            constraint=models.UniqueConstraint(fields=('area', 'approver'), name='unique_transfer_approver'),
        ),
        migrations.AddConstraint(
            model_name='budgettransferrelease',
            constraint=models.UniqueConstraint(fields=('transfer', 'transfer_approval_id'), name='unique_transfer_approval'),
        ),
    ]