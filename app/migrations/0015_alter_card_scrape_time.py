# Generated by Django 3.2.9 on 2022-10-11 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_mypreferences_location_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='scrape_time',
            field=models.IntegerField(default=0),
        ),
    ]
