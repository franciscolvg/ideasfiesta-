# Generated by Django 5.1.1 on 2024-10-04 01:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_articulo_cantidad_alter_articulo_id_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoria',
            name='nombre',
            field=models.CharField(max_length=100),
        ),
        migrations.CreateModel(
            name='Solicitud',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('apellido', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('telefono', models.CharField(max_length=20)),
                ('cedula', models.CharField(blank=True, max_length=20, null=True)),
                ('empresa', models.CharField(blank=True, max_length=100, null=True)),
                ('tipo_evento', models.CharField(max_length=100)),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField()),
                ('provincia', models.CharField(max_length=100)),
                ('direccion', models.TextField()),
                ('estado', models.CharField(choices=[('nueva', 'Nueva Solicitud'), ('revisada', 'Revisada'), ('en_ejecucion', 'En Ejecución'), ('finalizada', 'Finalizada'), ('rechazada', 'Rechazada')], default='nueva', max_length=20)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ArticuloSolicitud',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField(default=1)),
                ('articulo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.articulo')),
                ('solicitud', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='articulos', to='core.solicitud')),
            ],
        ),
    ]
