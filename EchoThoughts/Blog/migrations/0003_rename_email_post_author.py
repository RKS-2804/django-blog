# Generated by Django 5.1.5 on 2025-01-30 09:59

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("Blog", "0002_post_slug"),
    ]

    operations = [
        migrations.RenameField(
            model_name="post",
            old_name="email",
            new_name="author",
        ),
    ]
