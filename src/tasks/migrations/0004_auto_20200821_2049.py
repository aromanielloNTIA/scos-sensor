# Generated by Django 3.1 on 2020-08-21 20:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_auto_20200817_1815'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acquisition',
            name='data',
            field=models.FileField(null=True, upload_to='blob/%Y/%m/%d/%H/%M/%S'),
        ),
    ]