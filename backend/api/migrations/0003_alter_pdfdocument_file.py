# Generated by Django 5.1.7 on 2025-03-26 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_pdfdocument_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pdfdocument',
            name='file',
            field=models.FileField(upload_to=''),
        ),
    ]
