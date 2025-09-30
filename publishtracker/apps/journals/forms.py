# journals/forms.py
from django import forms
from .models import Revista, Editorial, CategoriaRevista, AmbitoRevista
from core.models import Pais # Asumiendo que está aquí

class RevistaForm(forms.ModelForm):
    class Meta:
        model = Revista
        fields = [
            'nombre',
            'issn_impreso',
            'issn_electronico',
            'factor_impacto',
            'editorial',
            'url',
            'pais_publicacion',
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
                'pattern': r'^\d{4}-\d{3}[\dX]$' # Patrón opcional para ISSN
            }),
            'issn_electronico': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ISSN Electrónico (opcional)',
                'pattern': r'^\d{4}-\d{3}[\dX]$' # Patrón opcional para ISSN
            }),
            'factor_impacto': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0',
                'placeholder': 'Factor de impacto (opcional)'
            }),
            'editorial': forms.Select(attrs={'class': 'form-select'}),
            'url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL de la revista (opcional)'
            }),
            'pais_publicacion': forms.Select(attrs={'class': 'form-select'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'ambito': forms.Select(attrs={'class': 'form-select'}),
            'dirigido_cuerpo_academico': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Opcional: Filtrar QuerySets si es necesario
        # self.fields['editorial'].queryset = Editorial.objects.filter(activo=True) # Si tienes un campo activo
        # self.fields['categoria'].queryset = CategoriaRevista.objects.filter(activo=True) # Si tienes un campo activo
        # self.fields['ambito'].queryset = AmbitoRevista.objects.filter(activo=True) # Si tienes un campo activo
        # self.fields['pais_publicacion'].queryset = Pais.objects.filter(activo=True) # Si tienes un campo activo

    # Opcional: Validaciones personalizadas
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        # Por ejemplo, asegurar unicidad (aunque el modelo ya la tiene)
        # if Revista.objects.filter(nombre__iexact=nombre).exists():
        #     raise forms.ValidationError('Ya existe una revista con ese nombre.')
        return nombre

    def clean(self):
        cleaned_data = super().clean()
        issn_impreso = cleaned_data.get('issn_impreso')
        issn_electronico = cleaned_data.get('issn_electronico')

        if not issn_impreso and not issn_electronico:
            raise forms.ValidationError('Debe ingresar al menos un ISSN (impreso o electrónico).')

        return cleaned_data
class PaisForm(forms.ModelForm):
    class Meta:
        model = Pais
        fields = ['nombre', 'codigo_iso'] # Agregamos codigo_iso
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del país'
            }),
            'codigo_iso': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código ISO (e.g. MEX, USA, GBR)',
                'maxlength': 3, # Limitar la longitud
                'style': 'text-transform: uppercase;' # Opcional: forzar mayúsculas en el input
            }),
        }

    # Opcional: Validaciones personalizadas
    def clean_codigo_iso(self):
        codigo = self.cleaned_data.get('codigo_iso')
        if codigo:
            # Asegurarse de que siempre esté en mayúsculas y sin espacios
            return codigo.strip().upper()
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
        fields = ['nombre', 'pais', 'direccion'] # Ajusta según los campos reales de tu modelo Editorial
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre de la editorial'
            }),
            'pais': forms.Select(attrs={'class': 'form-select'}), # Asumiendo que es ForeignKey
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese la dirección (opcional)',
                'rows': 2
            }),
        }