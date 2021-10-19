# Generated by Django 3.2.6 on 2021-10-18 00:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Author', '0004_alter_post_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='like',
            name='owner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='Author.user'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='post',
            name='type',
            field=models.SmallIntegerField(choices=[(4, 'UNLISTED'), (2, 'FRIEND ONLY'), (1, 'PUBLIC'), (3, 'PRIVATE')], default=1),
        ),
        migrations.CreateModel(
            name='Friend',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owner', to=settings.AUTH_USER_MODEL)),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
