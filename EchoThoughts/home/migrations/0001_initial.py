# Generated by Django 5.1.5 on 2025-01-29 10:27

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="contact",
            fields=[
                ("sno", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
                ("phone", models.CharField(max_length=13)),
                ("email", models.CharField(max_length=100)),
                ("content", models.TextField()),
            ],
        ),
    ]
