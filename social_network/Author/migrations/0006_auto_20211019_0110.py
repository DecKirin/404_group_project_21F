# Generated by Django 3.2.6 on 2021-10-19 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Author', '0005_auto_20211017_1852'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegisterControl',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('free_registration', models.BooleanField(default=True)),
            ],
        ),
        migrations.AlterField(
            model_name='post',
            name='type',
            field=models.SmallIntegerField(choices=[(2, 'FRIEND ONLY'), (1, 'PUBLIC'), (4, 'UNLISTED'), (3, 'PRIVATE')], default=1),
        ),
    ]