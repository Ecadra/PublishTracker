# catalogs/models.py
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator


class CatalogoBase(models.Model):
    """
    Clase base abstracta para catálogos del sistema.
    Define estructura común y consistencia en tablas maestras.
    """
    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre",
        help_text="Nombre descriptivo del elemento"
    )
    clave = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Clave",
        help_text="Identificador único alfanumérico"
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Define si el elemento está disponible para uso"
    )
    orden = models.PositiveIntegerField(
        default=0,
        verbose_name="Orden",
        help_text="Posición para ordenamiento (menor valor = mayor prioridad)"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción",
        help_text="Información adicional sobre el elemento"
    )
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        managed=True
        abstract = True
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre

    @property
    def activo_display(self):
        return "Activo" if self.activo else "Inactivo"

    def clean(self):
        """Normaliza datos antes de guardar"""
        if self.nombre:
            self.nombre = self.nombre.strip().title()
        if self.clave:
            self.clave = self.clave.strip().upper()


class TipoParticipacion(CatalogoBase):
    """Catálogo de tipos de participación en papers"""
    requiere_justificacion = models.BooleanField(
        default=False,
        verbose_name="Requiere Justificación",
        help_text="Define si se debe solicitar documentación adicional"
    )


class TipoCita(CatalogoBase):
    """Catálogo de tipos de citas bibliográficas"""
    color_interfaz = models.CharField(
        max_length=7,
        default="#007bff",
        verbose_name="Color de Interfaz",
        help_text="Color hexadecimal en formato #RRGGBB"
    )
    peso_metrico = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Peso Métrico",
        help_text="Factor de ponderación para cálculos de impacto"
    )


class FormatoArchivo(CatalogoBase):
    """Catálogo de formatos de archivo"""
    extension = models.CharField(
        max_length=10,
        verbose_name="Extensión",
        help_text="Extensión sin punto inicial (ej: pdf, docx)"
    )
    mime_type = models.CharField(
        max_length=100,
        verbose_name="Tipo MIME",
        help_text="Tipo MIME para validación (ej: application/pdf)"
    )
    tamaño_maximo_mb = models.PositiveIntegerField(
        default=10,
        verbose_name="Tamaño Máximo (MB)",
        help_text="Límite en megabytes"
    )

    

    def clean(self):
        """Normaliza la extensión (sin punto)"""
        if self.extension:
            self.extension = self.extension.strip().lower().replace(".", "")


class AreaConocimiento(CatalogoBase):
    """Catálogo jerárquico de áreas del conocimiento"""
    area_padre = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Área Padre",
        help_text="Área de conocimiento padre"
    )
    codigo_externo = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Código Externo",
        help_text="Código de clasificación externa (CONACYT, UNESCO, etc.)"
    )



    @property
    def nivel_jerarquia(self):
        """Nivel jerárquico del área (0 = raíz)"""
        nivel, area_actual = 0, self.area_padre
        while area_actual is not None:
            nivel += 1
            area_actual = area_actual.area_padre
        return nivel


class Institucion(CatalogoBase):
    """Catálogo de instituciones académicas y de investigación"""
    TIPOS_INSTITUCION = [
        ("UNIVERSIDAD", "Universidad"),
        ("CENTRO_INVESTIGACION", "Centro de Investigación"),
        ("EMPRESA_PRIVADA", "Empresa Privada"),
        ("ORGANISMO_PUBLICO", "Organismo Público"),
        ("ONG", "Organización No Gubernamental"),
    ]
    tipo_institucion = models.CharField(
        max_length=20,
        choices=TIPOS_INSTITUCION,
        default="UNIVERSIDAD",
        verbose_name="Tipo de Institución"
    )
    pais = models.ForeignKey(
        "core.Pais",
        on_delete=models.CASCADE,
        verbose_name="País"
    )
    sitio_web = models.URLField(
        blank=True,
        null=True,
        verbose_name="Sitio Web"
    )

    


class FuenteFinanciamiento(CatalogoBase):
    """Catálogo de fuentes de financiamiento para investigación"""
    TIPOS_FUENTE = [
        ("GUBERNAMENTAL", "Gubernamental"),
        ("INTERNACIONAL", "Internacional"),
        ("PRIVADA", "Empresa Privada"),
        ("MIXTA", "Público-Privada"),
        ("ACADEMICA", "Institución Académica"),
    ]
    tipo_fuente = models.CharField(
        max_length=15,
        choices=TIPOS_FUENTE,
        verbose_name="Tipo de Fuente"
    )
    monto_maximo = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Monto Máximo",
        help_text="Monto típico en pesos mexicanos"
    )
    vigente = models.BooleanField(
        default=True,
        verbose_name="Vigente",
        help_text="Si la fuente está actualmente disponible"
    )

    
