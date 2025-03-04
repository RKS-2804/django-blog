# Generated by Django 5.1.6 on 2025-02-11 13:57

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Blog", "backup_0007_remove_post_timestamp_alter_post_author_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="likes",
            field=models.ManyToManyField(
                blank=True, related_name="blog_likes", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
