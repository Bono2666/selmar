# Generated by Django 5.0 on 2024-02-24 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0012_areasales_base_city'),
    ]

    operations = [
        migrations.AddField(
            model_name='claim',
            name='depo',
            field=models.CharField(max_length=15, null=True),
        ),
    ]