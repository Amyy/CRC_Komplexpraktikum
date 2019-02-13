# Generated by Django 2.1.3 on 2018-12-07 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('image', '0012_image_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='count_userlabels',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='data',
            field=models.ImageField(null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='image',
            name='name',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='number',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='op',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='opset',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='variance',
            field=models.FloatField(null=True),
        ),
    ]
