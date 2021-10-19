# Generated by Django 3.2.6 on 2021-10-17 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Author', '0002_auto_20211014_2119'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'Author', 'verbose_name_plural': 'Author'},
        ),
        migrations.AddField(
            model_name='post',
            name='type',
            field=models.CharField(choices=[(1, 'PUBLIC'), (3, 'PRIVATE'), (2, 'FRIEND ONLY'), (4, 'UNLISTED')], default=1, max_length=20),
        ),
        migrations.AlterField(
            model_name='user',
            name='github',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='u_phone',
            field=models.CharField(blank=True, default='', max_length=20, verbose_name='phone_number'),
        ),
    ]
