# Generated by Django 2.2.2 on 2019-06-25 21:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0005_auto_20190625_1439'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tag',
            old_name='tag',
            new_name='slug',
        ),
    ]