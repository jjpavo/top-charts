# Generated by Django 2.2.2 on 2019-07-09 22:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('top_charts', '0004_auto_20190628_1536'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chart',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='top_charts.User'),
        ),
    ]
