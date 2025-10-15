# authors/forms.py

from django import forms
from .models import Autor

class AutorForm(forms.ModelForm):
    """
    Formulario para el modelo Autor.
    Permite ingresar el nombre y el ORCID del autor,
    aplicando validaciones y formateos definidos en el modelo.
    """
    class Meta:
        model = Autor
        fields = ['nombre', 'orcid']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre completo del autor'
            }),
            'orcid': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ORCID (opcional, e.g. 0000-0002-1825-0097)',
                'maxlength': 19,  # Longitud típica de ORCID
            }),
        }

    def clean_nombre(self):
        """
        Aplica el formateo del nombre usando el setter del modelo.
        """
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            autor_temp = Autor()
            autor_temp.set_nombre(nombre)
            return autor_temp.nombre  # Devuelve el nombre formateado
        return nombre

    def clean_orcid(self):
        """
        Aplica el formateo y validación del ORCID usando el setter del modelo.
        Lanza un error de validación si el ORCID no es válido.
        """
        orcid = self.cleaned_data.get('orcid')
        if orcid:
            autor_temp = Autor()
            try:
                autor_temp.set_orcid(orcid)
                return autor_temp.get_orcid()  # Devuelve el ORCID formateado
            except ValueError as e:
                raise forms.ValidationError(str(e))
        return orcid
