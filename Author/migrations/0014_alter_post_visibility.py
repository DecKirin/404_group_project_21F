# Generated by Django 3.2.8 on 2021-11-23 01:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Author', '0013_alter_post_visibility'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='visibility',
            field=models.SmallIntegerField(choices=[(2, 'FRIEND ONLY'), (1, 'PUBLIC'), (3, 'PRIVATE'), (4, 'UNLISTED')], default=1),
        ),
    ]