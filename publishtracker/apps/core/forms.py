from django import forms
from .models import ProgramaSeciti, EjeSecithi


class ProgramaSecitiForm(forms.ModelForm):
    """
    Formulario para la creación y edición de programas SECITI.

    Permite capturar y validar los datos básicos de un programa, como
    su nombre y descripción, aplicando estilos y placeholders
    personalizados para mejorar la experiencia del usuario.

    Attributes:
        Meta (type): Define el modelo, campos y widgets del formulario.
    """

    class Meta:
        model = ProgramaSeciti
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del programa SECITI'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese una descripción (opcional)',
                'rows': 2
            }),
        }


class EjeSecithiForm(forms.ModelForm):
    """
    Formulario para la creación y edición de ejes SECITHI.

    Permite ingresar el nombre y la descripción de un eje de trabajo
    dentro del programa SECITHI, garantizando una interfaz consistente
    con el resto de formularios del sistema.

    Attributes:
        Meta (type): Define el modelo, campos y widgets del formulario.
    """

    class Meta:
        model = EjeSecithi
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del eje SECITHI'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese una descripción (opcional)',
                'rows': 2
            }),
        }
