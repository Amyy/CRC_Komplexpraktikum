# Generated by Django 2.1.3 on 2018-12-07 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('image', '0014_auto_20181207_2041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='data',
            field=models.ImageField(default='default.jpg', null=True, upload_to=''),
        ),
    ]
