# Generated by Django 4.2.6 on 2023-11-09 22:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0007_budget_a1_date_budget_a1_id_budget_a1_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='budget',
            name='a1_date',
        ),
        migrations.RemoveField(
            model_name='budget',
            name='a1_id',
        ),
        migrations.RemoveField(
            model_name='budget',
            name='a1_name',
        ),
        migrations.RemoveField(
            model_name='budget',
            name='a1_position',
        ),
        migrations.RemoveField(
            model_name='budget',
            name='a1_status',
        ),
        migrations.RemoveField(
            model_name='budget',
            name='a2_date',
        ),
        migrations.RemoveField(
            model_name='budget',
            name='a2_id',
        ),
        migrations.RemoveField(
            model_name='budget',
            name='a2_name',
        ),
        migrations.RemoveField(
            model_name='budget',
            name='a2_position',
        ),
        migrations.RemoveField(
            model_name='budget',
            name='a2_status',
        ),
        migrations.CreateModel(
            name='BudgetRelease',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('budget_approval_id', models.CharField(max_length=50, null=True)),
                ('budget_approval_name', models.CharField(max_length=50, null=True)),
                ('budget_approval_position', models.CharField(max_length=50, null=True)),
                ('budget_approval_date', models.DateTimeField(null=True)),
                ('budget_approval_status', models.CharField(default='N', max_length=1)),
                ('entry_date', models.DateTimeField(null=True)),
                ('entry_by', models.CharField(max_length=50, null=True)),
                ('update_date', models.DateTimeField(null=True)),
                ('update_by', models.CharField(max_length=50, null=True)),
                ('budget', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apps.budget')),
            ],
        ),
        migrations.AddConstraint(
            model_name='budgetrelease',
            constraint=models.UniqueConstraint(fields=('budget', 'budget_approval_id'), name='unique_budget_approval'),
        ),
    ]