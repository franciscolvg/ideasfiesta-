# core/admin_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Articulo, Categoria, Solicitud, ArticuloSolicitud
from .forms import ArticuloForm, SolicitudForm, ArticuloSolicitudFormSet, ArticuloSolicitudForm
from django.http import JsonResponse
from django.db.models import Count, Sum, Q, F, Subquery, OuterRef
from django.utils import timezone
import logging
from django.forms import modelformset_factory


logger = logging.getLogger(__name__)

def is_staff(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff)
def admin_panel(request):
    return render(request, 'core/admin/panel.html')

@login_required
@user_passes_test(is_staff)
def admin_inventario(request):
    articulos = Articulo.objects.all().order_by('id')
    categorias = Categoria.objects.all()
    return render(request, 'core/admin/inventario.html', {
        'articulos': articulos,
        'categorias': categorias,
    })

# Al agregar
@login_required
@user_passes_test(is_staff)
def agregar_articulo(request):
    if request.method == 'POST':
        form = ArticuloForm(request.POST, request.FILES)
        if form.is_valid():
            codigo = form.cleaned_data.get('codigo')
            if Articulo.objects.filter(codigo=codigo).exists():
                form.add_error('codigo', 'Este código ya existe. Por favor, elige otro.')
            else:
                form.save()
                messages.success(request, 'Artículo agregado con éxito.')
                return redirect('admin_inventario')
    else:
        form = ArticuloForm()
    categorias = Categoria.objects.all().values_list('nombre', flat=True)
    return render(request, 'core/admin/agregar_articulo.html', {'form': form, 'categorias': list(categorias)})

# Al editar
@login_required
@user_passes_test(is_staff)
def editar_articulo(request, pk):
    articulo = get_object_or_404(Articulo, pk=pk)
    
    if request.method == 'POST':
        form = ArticuloForm(request.POST, request.FILES, instance=articulo)

        codigo = request.POST.get('codigo')
        if Articulo.objects.filter(codigo=codigo).exclude(pk=articulo.pk).exists():
            form.add_error('codigo', 'Este código ya está en uso por otro artículo.')

        if form.is_valid():
            form.save()
            messages.success(request, 'Artículo actualizado con éxito.')
            return redirect('admin_inventario')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = ArticuloForm(instance=articulo)

    categorias = Categoria.objects.all().values_list('nombre', flat=True)
    return render(request, 'core/admin/editar_articulo.html', {
        'form': form, 
        'articulo': articulo,
        'categorias': list(categorias)
    })

@login_required
@user_passes_test(is_staff)
def admin_solicitudes(request):
    estados = dict(Solicitud.ESTADO_CHOICES)
    solicitudes_por_estado = {}

    for estado, nombre in estados.items():
        solicitudes = Solicitud.objects.filter(estado=estado).order_by('-fecha_creacion')
        solicitudes_por_estado[estado] = solicitudes

    context = {
        'solicitudes_por_estado': solicitudes_por_estado,
        'estados': estados,
    }

    return render(request, 'core/admin/solicitudes.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def detalle_solicitud(request, pk):
    solicitud = get_object_or_404(Solicitud, pk=pk)
    articulos_solicitud = ArticuloSolicitud.objects.filter(solicitud=solicitud)
    
    # Calcular el precio total de los artículos solicitados
    total_precio = articulos_solicitud.aggregate(
        total=Sum(F('cantidad') * F('articulo__precio'))
    )['total'] or 0  # Asegurarse de que no sea None si no hay artículos
    
    # Debugging: Imprimir nombres y URLs de imágenes
    for articulo_solicitud in articulos_solicitud:
        print(f"Artículo: {articulo_solicitud.articulo.nombre}, Imagen URL: {articulo_solicitud.articulo.imagen.url if articulo_solicitud.articulo.imagen else 'No image'}")
    
    context = {
        'solicitud': solicitud,
        'articulos_solicitud': articulos_solicitud,
        'total_precio': total_precio  # Pasar el total al contexto
    }
    return render(request, 'core/admin/detalle_solicitud.html', context)

@login_required
@user_passes_test(is_staff)
def informe_solicitudes(request):
    total_solicitudes = Solicitud.objects.count()
    solicitudes_por_estado = Solicitud.objects.values('estado').annotate(total=Count('estado'))
    proximas_a_iniciar = Solicitud.objects.filter(
        fecha_inicio__gte=timezone.now(),
        fecha_inicio__lte=timezone.now() + timezone.timedelta(days=7)
    ).count()
    
    context = {
        'total_solicitudes': total_solicitudes,
        'solicitudes_por_estado': solicitudes_por_estado,
        'proximas_a_iniciar': proximas_a_iniciar,
    }
    return render(request, 'core/admin/informe_solicitudes.html', context)



# Definir el formset en la vista


@login_required
@user_passes_test(is_staff)
def crear_editar_solicitud(request, pk=None):
    solicitud = get_object_or_404(Solicitud, pk=pk) if pk else None

    ArticuloFormSet = modelformset_factory(ArticuloSolicitud, form=ArticuloSolicitudForm, extra=1, can_delete=True)

    if request.method == 'POST':
        solicitud_form = SolicitudForm(request.POST, instance=solicitud)
        articulo_formset = ArticuloFormSet(request.POST, queryset=ArticuloSolicitud.objects.filter(solicitud=solicitud))

        if solicitud_form.is_valid() and articulo_formset.is_valid():
            solicitud = solicitud_form.save(commit=False)
            solicitud.save()

            for form in articulo_formset:
                if form.cleaned_data.get('articulo'):
                    articulo_solicitud = form.save(commit=False)
                    articulo_solicitud.solicitud = solicitud
                    if form.cleaned_data.get('DELETE'):
                        articulo_solicitud.delete()
                    else:
                        articulo_solicitud.save()

            return redirect('admin_solicitudes')
    else:
        solicitud_form = SolicitudForm(instance=solicitud)
        articulo_formset = ArticuloFormSet(queryset=ArticuloSolicitud.objects.filter(solicitud=solicitud))

    # Obtener artículos disponibles para agregar
    articulos_disponibles = Articulo.objects.exclude(articulosolicitud__solicitud=solicitud)

    context = {
        'solicitud_form': solicitud_form,
        'articulo_formset': articulo_formset,
        'solicitud': solicitud,
        'articulos_disponibles': articulos_disponibles,  # Pasar los artículos disponibles a la plantilla
    }

    return render(request, 'core/admin/crear_editar_solicitud.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def informe_inventario(request):
    # Totales globales
    total_articulos = Articulo.objects.aggregate(total=Sum('cantidad'))['total'] or 0
    total_alquilados = ArticuloSolicitud.objects.filter(solicitud__estado='en_ejecucion').aggregate(total=Sum('cantidad'))['total'] or 0
    total_disponibles = total_articulos - total_alquilados

    # Subconsulta para contar los artículos alquilados en ejecución por categoría
    subquery_alquilados = ArticuloSolicitud.objects.filter(
        articulo__categoria=OuterRef('pk'),
        solicitud__estado='en_ejecucion'
    ).values('articulo__categoria').annotate(
        total_alquilados=Sum('cantidad')
    ).values('total_alquilados')

    # Anotar artículos y calcular totales por categoría
    categorias = Categoria.objects.annotate(
        total_articulos=Sum('articulo__cantidad'),
        total_alquilados=Subquery(subquery_alquilados)
    ).values('nombre', 'total_articulos', 'total_alquilados')

    for categoria in categorias:
        total_articulos_categoria = categoria['total_articulos'] or 0
        total_alquilados_categoria = categoria['total_alquilados'] or 0

        # Calculando los disponibles por categoría
        categoria['total_disponibles'] = total_articulos_categoria - total_alquilados_categoria

        # Agregar porcentajes al contexto
        categoria['porcentaje_total'] = (total_articulos_categoria / total_articulos) * 100 if total_articulos > 0 else 0
        categoria['porcentaje_alquilados'] = (total_alquilados_categoria / total_articulos_categoria) * 100 if total_articulos_categoria > 0 else 0
        categoria['porcentaje_disponibles'] = (categoria['total_disponibles'] / total_articulos_categoria) * 100 if total_articulos_categoria > 0 else 0

    context = {
        'total_articulos': total_articulos,
        'total_alquilados': total_alquilados,
        'total_disponibles': total_disponibles,
        'categorias': categorias,  # Pasar las categorías al contexto
    }

    return render(request, 'core/admin/informe_inventario.html', context)

@login_required
@user_passes_test(is_staff)
def eliminar_articulo(request, articulo_id):
    articulo = get_object_or_404(Articulo, id=articulo_id)
    articulo.delete()
    messages.success(request, "El artículo ha sido eliminado correctamente.")
    return redirect('admin_inventario')

@login_required
@user_passes_test(is_staff)
def check_id_availability(request):
    codigo = request.GET.get('codigo', None)  # Obtener el código de la consulta GET
    if codigo:
        is_taken = Articulo.objects.filter(codigo=codigo).exists()
        return JsonResponse({'is_taken': is_taken})
    return JsonResponse({'error': 'No se proporcionó código'}, status=400)
