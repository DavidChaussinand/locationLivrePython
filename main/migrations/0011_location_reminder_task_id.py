# Generated by Django 5.1.1 on 2024-10-01 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_inscription'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='reminder_task_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
