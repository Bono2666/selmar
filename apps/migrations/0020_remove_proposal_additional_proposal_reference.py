# Generated by Django 5.0 on 2024-03-18 00:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0019_program_header'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proposal',
            name='additional',
        ),
        migrations.AddField(
            model_name='proposal',
            name='reference',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
