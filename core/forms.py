# core/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Articulo, Categoria, SolicitudAlquiler, Solicitud, ArticuloSolicitud
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory


class ContactForm(forms.Form):
    nombre = forms.CharField(max_length=100)
    email = forms.EmailField()
    telefono = forms.CharField(max_length=15, required=False)
    mensaje = forms.CharField(widget=forms.Textarea)


class SolicitudAlquilerForm(forms.ModelForm):
    class Meta:
        model = SolicitudAlquiler
        fields = ['nombre', 'email', 'telefono', 'fecha_evento', 'mensaje']
        widgets = {
            'fecha_evento': forms.DateInput(attrs={'type': 'date'}),
        }


class SolicitudForm(forms.ModelForm):
    class Meta:
        model = Solicitud
        fields = [
            'nombre', 'apellido', 'email', 'telefono', 'cedula', 'empresa',
            'tipo_evento', 'fecha_inicio', 'fecha_fin', 'provincia', 'direccion', 'estado'
        ]
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(SolicitudForm, self).__init__(*args, **kwargs)
        # Hacer que el campo 'estado' no sea requerido
        self.fields['estado'].required = False
        
class ArticuloSolicitudForm(forms.ModelForm):
    class Meta:
        model = ArticuloSolicitud
        fields = ['articulo','cantidad']
        error_messages = {
            'cantidad': {
                'required': 'Por favor, ingrese una cantidad.',
            },
            'articulo': {
                'required': 'Por favor, seleccione un artículo.',
            }
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra solo los artículos con cantidad mayor a 0
        self.fields['articulo'].queryset = Articulo.objects.filter(cantidad__gt=0)

ArticuloSolicitudFormSet = inlineformset_factory(
    Solicitud,
    ArticuloSolicitud,
    fields=('articulo', 'cantidad'),
    extra=1,
    can_delete=True
)

class ArticuloForm(forms.ModelForm):
    nueva_categoria = forms.CharField(required=False, label="Nueva Categoría", help_text="Escribe una nueva categoría si no encuentras la que buscas.")

    class Meta:
        model = Articulo
        fields = ['nombre', 'descripcion', 'precio', 'cantidad', 'categoria', 'codigo', 'imagen']  # Incluir el campo 'codigo'
    
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get('instance', None)  # Mantener la instancia actual del artículo si se está editando
        super().__init__(*args, **kwargs)

    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')

        # Validar que el código sea único, pero ignorar la instancia actual si se está editando
        if Articulo.objects.filter(codigo=codigo).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Este código ya está en uso por otro artículo. Elija otro código.")

        return codigo

    def clean(self):
        cleaned_data = super().clean()
        nueva_categoria = cleaned_data.get('nueva_categoria')
        categoria = cleaned_data.get('categoria')

        # Si no se ha seleccionado una categoría existente y se ha proporcionado una nueva, crear la nueva categoría
        if not categoria and nueva_categoria:
            categoria, created = Categoria.objects.get_or_create(nombre=nueva_categoria)
            cleaned_data['categoria'] = categoria

        # Si no hay ni categoría seleccionada ni nueva categoría, mostrar un error
        elif not categoria and not nueva_categoria:
            self.add_error('categoria', "Debe seleccionar una categoría o crear una nueva.")
            self.add_error('nueva_categoria', "Debe seleccionar una categoría o crear una nueva.")

        return cleaned_data


# Crear el FormSet para los artículos
ArticuloFormSet = modelformset_factory(
    Articulo,  # El modelo del que se generará el FormSet
    fields=('nombre', 'descripcion', 'precio', 'cantidad', 'categoria', 'imagen'),  # Campos a incluir
    extra=1,  # Número de formularios extra a mostrar
    can_delete=True  # Permitir eliminar artículos
)
