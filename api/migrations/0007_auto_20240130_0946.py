# Generated by Django 3.2.23 on 2024-01-30 09:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_message_likes'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='privacy_setting',
            new_name='is_private',
        ),
        migrations.AlterField(
            model_name='notification',
            name='recipient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mynotification', to=settings.AUTH_USER_MODEL),
        ),
    ]