# Generated by Django 5.1.3 on 2024-11-20 03:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_app', '0004_alter_quiz_end_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='choice',
            name='points',
        ),
    ]
