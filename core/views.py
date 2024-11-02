from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ContactForm, SolicitudAlquilerForm, SolicitudForm, ArticuloForm
from .models import Articulo, Categoria, SolicitudAlquiler, Solicitud, ArticuloSolicitud
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from django.core.exceptions import ValidationError
from django.db import transaction
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import logout


def custom_logout(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('home')

class CustomLoginView(LoginView):
    template_name = 'core/login.html'
    success_url = reverse_lazy('admin_panel')

def home(request):
    articulos_destacados = Articulo.objects.all()[:3]
    return render(request, 'core/home.html', {'articulos_destacados': articulos_destacados})


def contacto(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Obtener los datos del formulario
            nombre = form.cleaned_data['nombre']
            email = form.cleaned_data['email']
            mensaje = form.cleaned_data['mensaje']
            telefono = form.cleaned_data.get('telefono', None)  # Campo opcional

            # Enviar correo electrónico
            subject = 'Nuevo mensaje de contacto'
            message = f'Nombre: {nombre}\nEmail: {email}\nMensaje: {mensaje}\nTeléfono: {telefono or "No proporcionado"}'
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                ['franciscolvg04@gmail.com'],  # correo que recibirá el mensaje
                fail_silently=False,
            )

            messages.success(request, 'Gracias por contactarnos. Hemos recibido tu mensaje y te responderemos pronto.')

            return redirect('contacto')
    else:
        form = ContactForm()  # Mostrar el formulario vacío

    # Cargar la plantilla de contacto con el formulario
    return render(request, 'core/contacto.html', {'form': form})

def catalogo(request):
    categoria_id = request.GET.get('categoria')
    search_query = request.GET.get('search')

    articulos = Articulo.objects.all()

    if categoria_id:
        articulos = articulos.filter(categoria_id=categoria_id)
    
    if search_query:
        articulos = articulos.filter(
            Q(nombre__icontains=search_query) | 
            Q(descripcion__icontains=search_query)
        )

    categorias = Categoria.objects.annotate(num_articulos=Count('articulo')).filter(num_articulos__gt=0)

    context = {
        'articulos': articulos,
        'categorias': categorias,
        'categoria_actual': int(categoria_id) if categoria_id else None,
        'search_query': search_query
    }

    return render(request, 'core/catalogo.html', context)

def quienes_somos(request):
    return render(request, 'core/quienes_somos.html')

def nuestros_clientes(request):
    return render(request, 'core/nuestros_clientes.html')

def carrito(request):
    carrito = request.session.get('carrito', {})
    articulos = Articulo.objects.filter(id__in=carrito.keys())
    
    for articulo in articulos:
        articulo.cantidad_carrito = carrito.get(str(articulo.id), 0)

    total = sum(articulo.precio * articulo.cantidad_carrito for articulo in articulos)
    
    return render(request, 'core/carrito.html', {
        'articulos': articulos,
        'carrito': carrito,
        'total': total
    })

def carrito_lateral(request):
    carrito = request.session.get('carrito', {})
    articulos = Articulo.objects.filter(id__in=carrito.keys())
    for articulo in articulos:
        articulo.cantidad = carrito.get(str(articulo.id), 0)
    return render(request, 'core/carrito_lateral.html', {'articulos': articulos})

@require_POST
def agregar_al_carrito(request, articulo_id):
    articulo = get_object_or_404(Articulo, id=articulo_id)
    carrito = request.session.get('carrito', {})
    nueva_cantidad = int(request.POST.get('cantidad', 1))

    carrito[str(articulo_id)] = nueva_cantidad
    request.session['carrito'] = carrito

    return JsonResponse({'success': True, 'nueva_cantidad': carrito[str(articulo_id)]})

@require_POST
def quitar_del_carrito(request, articulo_id):
    carrito = request.session.get('carrito', {})
    if str(articulo_id) in carrito:
        del carrito[str(articulo_id)]
        request.session['carrito'] = carrito
        request.session.modified = True
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@require_POST
def actualizar_cantidad_carrito(request):
    articulo_id = request.POST.get('articulo_id')
    nueva_cantidad = request.POST.get('cantidad')

    try:
        nueva_cantidad = int(nueva_cantidad)
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'Cantidad inválida'})

    if nueva_cantidad < 1:
        return JsonResponse({'success': False, 'error': 'La cantidad debe ser al menos 1'})

    carrito = request.session.get('carrito', {})
    if str(articulo_id) in carrito:
        carrito[str(articulo_id)] = nueva_cantidad
        request.session['carrito'] = carrito
        request.session.modified = True
        return JsonResponse({'success': True, 'nueva_cantidad': nueva_cantidad})

    return JsonResponse({'success': False, 'error': 'Artículo no encontrado en el carrito'})

def obtener_total_carrito(request):
    carrito = request.session.get('carrito', {})
    total = sum(
        Articulo.objects.get(id=int(articulo_id)).precio * cantidad
        for articulo_id, cantidad in carrito.items()
    )
    return JsonResponse({'total': total})

@transaction.atomic
def solicitud_alquiler(request):
    if request.method == 'POST':
        form = SolicitudAlquilerForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            carrito = request.session.get('carrito', {})
            
            if not carrito:
                messages.error(request, 'No hay artículos en el carrito.')
                return redirect('carrito')

            solicitud.save()
            solicitud.articulos.set(Articulo.objects.filter(id__in=carrito.keys()))

            request.session['carrito'] = {}
            request.session.modified = True

            messages.success(request, 'Solicitud de alquiler enviada con éxito.')
            return redirect('home')
    else:
        form = SolicitudAlquilerForm()
    return render(request, 'core/solicitud_alquiler.html', {'form': form})

@transaction.atomic
def crear_solicitud(request):
    if request.method == 'POST':
        solicitud = Solicitud(
            nombre=request.POST['nombre'],
            apellido=request.POST['apellido'],
            email=request.POST['email'],
            telefono=request.POST['telefono'],
            cedula=request.POST.get('cedula', ''),  # Campo opcional
            empresa=request.POST.get('empresa', ''),  # Campo opcional
            tipo_evento=request.POST['tipo_evento'],
            fecha_inicio=request.POST['fecha_inicio'],
            fecha_fin=request.POST['fecha_fin'],
            provincia=request.POST['provincia'],
            direccion=request.POST['direccion'],
            usuario=request.user if request.user.is_authenticated else None,
            estado='nueva'
        )
        solicitud.save()

        carrito = request.session.get('carrito', {})
        if not carrito:
            messages.error(request, 'No hay artículos en el carrito.')
            return redirect('carrito')

        for articulo_id, cantidad in carrito.items():
            articulo = get_object_or_404(Articulo, id=articulo_id)
            ArticuloSolicitud.objects.create(
                solicitud=solicitud,
                articulo=articulo,
                cantidad=cantidad
            )

        request.session['carrito'] = {}
        request.session.modified = True

        messages.success(request, 'Solicitud enviada con éxito.')
        return redirect('home')

    return redirect('carrito')

def agregar_editar_articulo(request, articulo_id=None):
    if articulo_id:
        articulo = get_object_or_404(Articulo, id=articulo_id)
    else:
        articulo = None

    if request.method == 'POST':
        form = ArticuloForm(request.POST, request.FILES, instance=articulo)
        if form.is_valid():
            form.save()
            return redirect('lista_articulos')
    else:
        form = ArticuloForm(instance=articulo)

    return render(request, 'core/agregar_articulo.html', {'form': form, 'articulo': articulo})

def admin_solicitudes(request):
    estados = {
        'nueva': 'Nuevas',
        'en_proceso': 'En Proceso',
        'completada': 'Completadas',
        'cancelada': 'Canceladas',
    }

    solicitudes_por_estado = {
        estado: Solicitud.objects.filter(estado=estado)
        for estado in estados.keys()
    }

    return render(request, 'admin/solicitudes.html', {
        'solicitudes_por_estado': solicitudes_por_estado,
        'estados': estados,
    })


from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client
from django.shortcuts import render, redirect
from .forms import ContactForm
from django.contrib import messages
from .forms import ContactForm, SolicitudAlquilerForm, SolicitudForm, ArticuloForm

