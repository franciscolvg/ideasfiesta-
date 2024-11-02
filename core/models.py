from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Articulo(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=100, unique=True, default='default_code')  # Default temporal
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.IntegerField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='articulos/', null=True, blank=True)

    def __str__(self):
        return self.nombre

class Solicitud(models.Model):
    ESTADO_CHOICES = [
        ('nueva', 'Nueva'),
        ('revisada', 'Revisada'),
        ('en_ejecucion', 'En Ejecución'),
        ('finalizada', 'Finalizada'),
        ('rechazada', 'Rechazada'),
    ]
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='nueva', blank=True, null=True)

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    cedula = models.CharField(max_length=20, blank=True, null=True)
    empresa = models.CharField(max_length=100, blank=True, null=True)
    tipo_evento = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    provincia = models.CharField(max_length=100)
    direccion = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='nueva')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Solicitud de {self.nombre} {self.apellido} - {self.get_estado_display()}"

class ArticuloSolicitud(models.Model):
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='articulos')
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad} x {self.articulo.nombre} para {self.solicitud}"

class SolicitudAlquiler(models.Model):
    nombre = models.CharField(max_length=200)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    fecha_evento = models.DateField()
    mensaje = models.TextField()
    articulos = models.ManyToManyField(Articulo)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Solicitud de {self.nombre} - {self.fecha_solicitud}" 
    
#para enviar email debe quitar el acomentari en settings.py de lo siguiente 

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.example.com'  # El servidor SMTP de tu proveedor
# EMAIL_PORT = 587  # O el puerto que use tu proveedor
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'tu-email@example.com'
# EMAIL_HOST_PASSWORD = 'tu-contraseña'

#para enviar email debe quitar el acomentari aqui en models.py
#@receiver(post_save, sender=Solicitud)
#def notificar_nueva_solicitud(sender, instance, created, **kwargs):
    #if created:
        #send_mail(
            #'Nueva solicitud de alquiler',
            #f'Se ha creado una nueva solicitud de alquiler con ID {instance.id}',
            #'from@example.com',
            #['admin@example.com'],
            #fail_silently=False,
        #)