# journals/forms.py
from django import forms
from .models import Revista, Editorial, CategoriaRevista, AmbitoRevista
from core.models import Pais


class RevistaForm(forms.ModelForm):
    class Meta:
        model = Revista
        fields = [
            'nombre',
            'issn_impreso',
            'issn_electronico',
            'factor_impacto',
            'pais_publicacion',
            'editorial',
            'url',
            'categoria',
            'ambito',
            'dirigido_cuerpo_academico',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre de la revista'
            }),
            'issn_impreso': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ISSN Impreso (opcional)',
                'pattern': r'^\d{4}-\d{3}[\dX]$'
            }),
            'issn_electronico': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ISSN Electrónico (opcional)',
                'pattern': r'^\d{4}-\d{3}[\dX]$'
            }),
            'factor_impacto': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0',
                'placeholder': 'Factor de impacto (opcional)'
            }),
            'pais_publicacion': forms.Select(attrs={'class': 'form-select'}),
            'editorial': forms.Select(attrs={'class': 'form-select'}),
            'url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL de la revista (opcional)'
            }),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'ambito': forms.Select(attrs={'class': 'form-select'}),
            'dirigido_cuerpo_academico': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Inicializar el formulario de Revista.
        Pasos:
        1. Llamar al inicializador de la clase base
        2. Configurar QuerySets opcionales (si aplica)
        """
        # 1. Llamar al inicializador de la clase base
        super().__init__(*args, **kwargs)

        # 2. Configurar QuerySets opcionales (si aplica)
        # self.fields['editorial'].queryset = Editorial.objects.filter(activo=True)
        # self.fields['categoria'].queryset = CategoriaRevista.objects.filter(activo=True)
        # self.fields['ambito'].queryset = AmbitoRevista.objects.filter(activo=True)
        # self.fields['pais_publicacion'].queryset = Pais.objects.filter(activo=True)

    def clean_nombre(self):
        """
        Validar el nombre de la revista.
        Pasos:
        1. Obtener el valor de nombre
        2. Validar reglas de negocio (si aplica)
        3. Retornar el nombre limpio
        """
        # 1. Obtener el valor de nombre
        nombre = self.cleaned_data.get('nombre')

        # 2. Validar reglas de negocio (si aplica)
        # if Revista.objects.filter(nombre__iexact=nombre).exists():
        #     raise forms.ValidationError('Ya existe una revista con ese nombre.')

        # 3. Retornar el nombre limpio
        return nombre

    def clean(self):
        """
        Validar coherencia de ISSN impreso/electrónico.
        Pasos:
        1. Llamar a la limpieza base
        2. Obtener los ISSN ingresados
        3. Validar que al menos uno esté presente
        4. Retornar los datos limpios
        """
        # 1. Llamar a la limpieza base
        cleaned_data = super().clean()

        # 2. Obtener los ISSN ingresados
        issn_impreso = cleaned_data.get('issn_impreso')
        issn_electronico = cleaned_data.get('issn_electronico')

        # 3. Validar que al menos uno esté presente
        if not issn_impreso and not issn_electronico:
            raise forms.ValidationError('Debe ingresar al menos un ISSN (impreso o electrónico).')

        # 4. Retornar los datos limpios
        return cleaned_data


class PaisForm(forms.ModelForm):
    class Meta:
        model = Pais
        fields = ['nombre', 'codigo_iso']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del país'
            }),
            'codigo_iso': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código ISO (e.g. MEX, USA, GBR)',
                'maxlength': 3,
                'style': 'text-transform: uppercase;'
            }),
        }

    def clean_codigo_iso(self):
        """
        Normalizar el código ISO del país.
        Pasos:
        1. Obtener el código ingresado
        2. Limpiar espacios y convertir a mayúsculas
        3. Retornar el código normalizado
        """
        # 1. Obtener el código ingresado
        codigo = self.cleaned_data.get('codigo_iso')

        # 2. Limpiar espacios y convertir a mayúsculas
        if codigo:
            codigo = codigo.strip().upper()

        # 3. Retornar el código normalizado
        return codigo


class CategoriaRevistaForm(forms.ModelForm):
    class Meta:
        model = CategoriaRevista
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre de la categoría'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese una descripción (opcional)',
                'rows': 2
            }),
        }


class AmbitoRevistaForm(forms.ModelForm):
    class Meta:
        model = AmbitoRevista
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del ámbito'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese una descripción (opcional)',
                'rows': 2
            }),
        }


class EditorialForm(forms.ModelForm):
    class Meta:
        model = Editorial
        fields = ['nombre', 'pais', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre de la editorial'
            }),
            'pais': forms.Select(attrs={'class': 'form-select'}),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese la dirección (opcional)',
                'rows': 2
            }),
        }
