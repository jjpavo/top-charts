# Generated by Django 2.2.1 on 2019-06-28 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('top_charts', '0003_croppedimage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='tags',
        ),
        migrations.AddField(
            model_name='tag',
            name='tag',
            field=models.CharField(default='', max_length=250, unique=True),
        ),
    ]