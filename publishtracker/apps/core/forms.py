from django import forms
from .models import ProgramaSeciti, EjeSecithi

class ProgramaSecitiForm(forms.ModelForm):
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