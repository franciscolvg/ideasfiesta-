# Generated by Django 5.1.1 on 2024-10-08 03:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_articulo_codigo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='articulo',
            name='codigo',
        ),
    ]
