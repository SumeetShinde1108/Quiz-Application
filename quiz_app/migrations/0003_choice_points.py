# Generated by Django 5.1.3 on 2024-11-19 02:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_app', '0002_alter_leaderboard_rank'),
    ]

    operations = [
        migrations.AddField(
            model_name='choice',
            name='points',
            field=models.IntegerField(default=0),
        ),
    ]
