from django.contrib import admin

# Register your models here.

from .models import Categoria, Articulo, SolicitudAlquiler

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'categoria')
    list_filter = ('categoria',)
    search_fields = ('nombre', 'descripcion')

@admin.register(SolicitudAlquiler)
class SolicitudAlquilerAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'fecha_evento', 'fecha_solicitud')
    list_filter = ('fecha_evento', 'fecha_solicitud')
    search_fields = ('nombre', 'email')