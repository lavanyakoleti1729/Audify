# Generated by Django 5.0.dev20230120115851 on 2023-06-24 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('converter', '0004_comment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='video',
            new_name='audio',
        ),
        migrations.AlterField(
            model_name='comment',
            name='timestamp',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
