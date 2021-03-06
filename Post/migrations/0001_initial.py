# Generated by Django 3.2.8 on 2021-12-06 20:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Author', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PostLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('published', models.DateTimeField(auto_now_add=True)),
                ('author', models.JSONField(default=dict, max_length=2000)),
                ('object', models.URLField()),
                ('summary', models.CharField(max_length=120)),
                ('post', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='post_like', to='Author.post')),
                ('who_like', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='likes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'likes',
            },
        ),
        migrations.CreateModel(
            name='PostComment',
            fields=[
                ('id_comment', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True)),
                ('author', models.JSONField(blank=True, default=dict, max_length=2000, null=True)),
                ('comment', models.TextField()),
                ('published', models.DateTimeField(auto_now_add=True)),
                ('url', models.URLField(default='', editable=False)),
                ('api_url', models.URLField(default='', editable=False)),
                ('author_comment', models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='Author.post')),
            ],
            options={
                'db_table': 'postcomment',
                'ordering': ('published',),
            },
        ),
    ]
