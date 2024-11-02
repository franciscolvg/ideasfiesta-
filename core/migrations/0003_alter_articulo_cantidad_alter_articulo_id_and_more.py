# Generated by Django 5.1.1 on 2024-10-03 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_articulo_cantidad'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articulo',
            name='cantidad',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='articulo',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='articulo',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='articulos/'),
        ),
        migrations.AlterField(
            model_name='categoria',
            name='nombre',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
