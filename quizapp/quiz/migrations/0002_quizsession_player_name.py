# Generated by Django 5.1.4 on 2024-12-12 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizsession',
            name='player_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
