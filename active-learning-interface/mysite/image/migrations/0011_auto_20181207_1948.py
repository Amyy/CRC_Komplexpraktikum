# Generated by Django 2.1.3 on 2018-12-07 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('image', '0010_label_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='op',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='image',
            name='opset',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
