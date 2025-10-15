# authors/forms.py

from django import forms
from .models import Autor


class AutorForm(forms.ModelForm):
    """
    Formulario de captura y validación para el modelo Autor.

    Proporciona campos para nombre y ORCID, aplicando las reglas de
    formateo y validación definidas en el propio modelo mediante sus
    setters/getters.

    Attributes:
        Meta (type): Define `model`, `fields` y `widgets` del formulario.
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
        Normaliza y valida el campo `nombre` usando la lógica del modelo.

        Usa el setter `Autor.set_nombre` para aplicar el formateo centralizado
        en el modelo y devolver el valor ya normalizado.

        Returns:
            str | None: Nombre formateado si se proporcionó; de lo contrario,
            el valor original (posiblemente `None`).
        """
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            autor_temp = Autor()
            autor_temp.set_nombre(nombre)
            return autor_temp.nombre  # Devuelve el nombre formateado
        return nombre

    def clean_orcid(self):
        """
        Normaliza y valida el campo `orcid` usando la lógica del modelo.

        Invoca `Autor.set_orcid` para validar formato y consistencia del
        identificador, y `Autor.get_orcid` para retornar el valor formateado.

        Returns:
            str | None: ORCID formateado si se proporcionó; de lo contrario,
            el valor original (posiblemente `None`).

        Raises:
            django.forms.ValidationError: Si el ORCID es inválido según las
            reglas del modelo.
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
