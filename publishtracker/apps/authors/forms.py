# authors/forms.py
from django import forms
from .models import Autor

class AutorForm(forms.ModelForm):
    class Meta:
        model = Autor
        fields = ['nombre', 'orcid'] # Incluye los campos que deseas que el usuario llene
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre completo del autor'
            }),
            'orcid': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ORCID (opcional, e.g. 0000-0002-1825-0097)',
                'maxlength': 19, # Longitud típica de ORCID
            }),
        }

    # Opcional: Sobrescribir el clean para aplicar los setters del modelo
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            # Usamos el setter del modelo para formatear
            autor_temp = Autor()
            autor_temp.set_nombre(nombre)
            return autor_temp.nombre # Devuelve el nombre ya formateado
        return nombre

    def clean_orcid(self):
        orcid = self.cleaned_data.get('orcid')
        if orcid:
            try:
                # Usamos el setter del modelo para formatear
                autor_temp = Autor()
                autor_temp.set_orcid(orcid)
                return autor_temp.get_orcid() # Devuelve el ORCID ya formateado
            except ValueError as e:
                raise forms.ValidationError(str(e))
        return orcid
