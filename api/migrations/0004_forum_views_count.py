# Generated by Django 3.2.23 on 2024-01-24 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20240124_1825'),
    ]

    operations = [
        migrations.AddField(
            model_name='forum',
            name='views_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]