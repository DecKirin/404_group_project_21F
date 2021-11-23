# Generated by Django 3.2.8 on 2021-11-23 01:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Author', '0011_auto_20211122_1834'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='visibility',
            field=models.SmallIntegerField(choices=[(3, 'PRIVATE'), (4, 'UNLISTED'), (2, 'FRIEND ONLY'), (1, 'PUBLIC')], default=1),
        ),
    ]