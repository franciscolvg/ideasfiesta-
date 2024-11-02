from django.urls import path
from . import views, admin_views
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    # Páginas del menú
    path('', views.home, name='home'),
    path('contacto/', views.contacto, name='contacto'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('quienes-somos/', views.quienes_somos, name='quienes_somos'),
    path('nuestros-clientes/', views.nuestros_clientes, name='nuestros_clientes'),
    path('carrito/', views.carrito, name='carrito'),
    
    # Carrito lateral
    path('carrito-lateral/', views.carrito_lateral, name='carrito_lateral'),
    path('agregar-al-carrito/<int:articulo_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('actualizar-cantidad-carrito/', views.actualizar_cantidad_carrito, name='actualizar_cantidad_carrito'),
    path('quitar-del-carrito/<int:articulo_id>/', views.quitar_del_carrito, name='quitar_del_carrito'),
    path('obtener-total-carrito/', views.obtener_total_carrito, name='obtener_total_carrito'),
    
    # Solicitud de alquiler del cliente
    path('solicitud-alquiler/', views.solicitud_alquiler, name='solicitud_alquiler'),
    path('crear-solicitud/', views.crear_solicitud, name='crear_solicitud'),  # Crear solicitud desde el cliente

    # Autenticación
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),

    # Panel de administración
    path('panel/', admin_views.admin_panel, name='admin_panel'),
    path('panel/inventario/', admin_views.admin_inventario, name='admin_inventario'),
    path('panel/agregar-articulo/', admin_views.agregar_articulo, name='agregar_articulo'),
    path('check-id-availability/', admin_views.check_id_availability, name='check_id_availability'),
    path('panel/editar-articulo/<int:pk>/', admin_views.editar_articulo, name='editar_articulo'),
    path('articulo/eliminar/<int:articulo_id>/', admin_views.eliminar_articulo, name='eliminar_articulo'),
    path('check-id-availability/', admin_views.check_id_availability, name='check_id_availability'),


  # Solicitudes en el panel de administración
    path('panel/solicitudes/', admin_views.admin_solicitudes, name='admin_solicitudes'),
    path('panel/solicitudes/crear/', admin_views.crear_editar_solicitud, name='admin_crear_solicitud'),
    path('panel/solicitudes/editar/<int:pk>/', admin_views.crear_editar_solicitud, name='admin_editar_solicitud'),
    path('panel/solicitudes/detalle/<int:pk>/', admin_views.detalle_solicitud, name='detalle_solicitud'),

    # Informes
    path('panel/informe/', admin_views.informe_solicitudes, name='informe_solicitudes'),
    path('panel/inventario/informe/', admin_views.informe_inventario, name='informe_inventario'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)