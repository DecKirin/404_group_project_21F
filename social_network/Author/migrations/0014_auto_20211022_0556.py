# Generated by Django 3.1.6 on 2021-10-22 05:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Author', '0013_auto_20211022_0554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='type',
            field=models.SmallIntegerField(choices=[(4, 'UNLISTED'), (2, 'FRIEND ONLY'), (1, 'PUBLIC'), (3, 'PRIVATE')], default=1),
        ),
    ]