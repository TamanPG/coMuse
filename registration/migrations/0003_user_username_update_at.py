# Generated by Django 5.0.7 on 2025-02-02 02:51

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("registration", "0002_friendship_friendship_follow_unique"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="username_update_at",
            field=models.DateField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]
