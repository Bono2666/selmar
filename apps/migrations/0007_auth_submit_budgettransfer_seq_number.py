# Generated by Django 5.0 on 2024-02-20 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0006_budgettransfer_budgettransfermatrix_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='auth',
            name='submit',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='budgettransfer',
            name='seq_number',
            field=models.IntegerField(default=0),
        ),
    ]
