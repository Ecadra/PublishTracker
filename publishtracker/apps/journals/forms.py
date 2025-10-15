from django import forms
from .models import Revista, Editorial, CategoriaRevista, AmbitoRevista
from core.models import Pais


class RevistaForm(forms.ModelForm):
    """
    Formulario para la creación y edición de revistas académicas.

    Permite registrar o modificar la información general de una revista,
    incluyendo ISSN, país de publicación, editorial, categoría y otros
    campos relacionados.

    Attributes:
        Meta (type): Define el modelo `Revista`, sus campos y widgets asociados.
    """

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
        Inicializa el formulario `RevistaForm`.

        Configura los conjuntos de datos (QuerySets) de los campos selectivos,
        si se requiere, filtrando únicamente los registros activos.
        """
        super().__init__(*args, **kwargs)
        # Ejemplo de configuración opcional:
        # self.fields['editorial'].queryset = Editorial.objects.filter(activo=True)
        # self.fields['categoria'].queryset = CategoriaRevista.objects.filter(activo=True)
        # self.fields['ambito'].queryset = AmbitoRevista.objects.filter(activo=True)
        # self.fields['pais_publicacion'].queryset = Pais.objects.filter(activo=True)

    def clean_nombre(self):
        """
        Valida el campo `nombre` de la revista.

        Garantiza que el nombre esté normalizado y, opcionalmente,
        evita duplicados.

        Returns:
            str: Nombre validado de la revista.
        """
        nombre = self.cleaned_data.get('nombre')
        # if Revista.objects.filter(nombre__iexact=nombre).exists():
        #     raise forms.ValidationError('Ya existe una revista con ese nombre.')
        return nombre

    def clean(self):
        """
        Valida la coherencia entre los campos ISSN impreso y electrónico.

        Exige que al menos uno de los dos ISSN esté presente antes de guardar.

        Returns:
            dict: Datos limpios y validados.

        Raises:
            forms.ValidationError: Si ambos campos ISSN están vacíos.
        """
        cleaned_data = super().clean()
        issn_impreso = cleaned_data.get('issn_impreso')
        issn_electronico = cleaned_data.get('issn_electronico')

        if not issn_impreso and not issn_electronico:
            raise forms.ValidationError('Debe ingresar al menos un ISSN (impreso o electrónico).')
        return cleaned_data


class PaisForm(forms.ModelForm):
    """
    Formulario para registrar o editar países.

    Permite ingresar el nombre y el código ISO (3 letras),
    aplicando normalización automática al código.

    Attributes:
        Meta (type): Define el modelo `Pais`, campos y widgets asociados.
    """

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
        Normaliza el código ISO del país antes de validarlo.

        Returns:
            str: Código ISO en mayúsculas y sin espacios.
        """
        codigo = self.cleaned_data.get('codigo_iso')
        if codigo:
            codigo = codigo.strip().upper()
        return codigo


class CategoriaRevistaForm(forms.ModelForm):
    """
    Formulario para la creación o edición de categorías de revista.

    Attributes:
        Meta (type): Define el modelo `CategoriaRevista`, campos y widgets.
    """

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
    """
    Formulario para la creación o edición de ámbitos de revista.

    Attributes:
        Meta (type): Define el modelo `AmbitoRevista`, campos y widgets.
    """

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
    """
    Formulario para registrar o editar editoriales de revistas.

    Permite capturar información básica de la editorial,
    como nombre, país y dirección.

    Attributes:
        Meta (type): Define el modelo `Editorial`, campos y widgets.
    """

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
