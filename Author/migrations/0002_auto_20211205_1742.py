# Generated by Django 3.2.8 on 2021-12-06 00:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Author', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='api_url',
            field=models.URLField(),
        ),
        migrations.AlterField(
            model_name='user',
            name='host',
            field=models.URLField(),
        ),
        migrations.AlterField(
            model_name='user',
            name='url',
            field=models.URLField(),
        ),
    ]