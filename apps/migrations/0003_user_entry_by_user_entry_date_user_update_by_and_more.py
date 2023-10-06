# Generated by Django 4.2.4 on 2023-10-03 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0002_remove_user_entry_by_remove_user_entry_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='entry_by',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='entry_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='update_by',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='update_date',
            field=models.DateTimeField(null=True),
        ),
    ]
