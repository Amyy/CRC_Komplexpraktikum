# Generated by Django 2.1.3 on 2018-12-18 17:27

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('image', '0016_auto_20181216_1301'),
    ]

    operations = [
        migrations.AddField(
            model_name='userlabels',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]