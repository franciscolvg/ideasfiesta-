# Generated by Django 5.1.1 on 2024-10-08 03:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_remove_articulo_codigo'),
    ]

    operations = [
        migrations.AddField(
            model_name='articulo',
            name='codigo',
            field=models.CharField(default='default_code', max_length=100, unique=True),
        ),
    ]