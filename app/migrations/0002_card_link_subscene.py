# Generated by Django 3.2.9 on 2022-09-15 04:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='link_subscene',
            field=models.URLField(blank=True, null=True),
        ),
    ]
