from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator


class CatalogoBase(models.Model):
    """
    Clase base abstracta para catálogos del sistema.

    Define una estructura estandarizada para tablas maestras, incluyendo
    campos comunes como `nombre`, `clave`, `activo`, y fechas de control.

    Attributes:
        nombre (str): Nombre descriptivo del elemento.
        clave (str): Identificador único alfanumérico.
        activo (bool): Indica si el elemento está disponible para uso.
        orden (int): Valor numérico para ordenamiento (menor = mayor prioridad).
        descripcion (str): Información adicional del elemento.
        fecha_creacion (datetime): Fecha de creación del registro.
        fecha_modificacion (datetime): Fecha de última modificación.
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
        managed = True
        abstract = True
        ordering = ["orden", "nombre"]

    def __str__(self):
        """Retorna el nombre legible del catálogo."""
        return self.nombre

    @property
    def activo_display(self):
        """
        Devuelve una representación legible del estado activo.

        Returns:
            str: "Activo" si el elemento está habilitado, "Inactivo" si no.
        """
        return "Activo" if self.activo else "Inactivo"

    def clean(self):
        """
        Normaliza los valores de los campos antes de guardar.

        Ajusta capitalización y elimina espacios innecesarios.
        """
        if self.nombre:
            self.nombre = self.nombre.strip().title()
        if self.clave:
            self.clave = self.clave.strip().upper()


class TipoParticipacion(CatalogoBase):
    """
    Catálogo de tipos de participación en publicaciones académicas.

    Indica si un tipo de participación requiere documentación adicional.
    
    Attributes:
        requiere_justificacion (bool): Determina si se requiere justificación.
    """
    requiere_justificacion = models.BooleanField(
        default=False,
        verbose_name="Requiere Justificación",
        help_text="Define si se debe solicitar documentación adicional"
    )


class TipoCita(CatalogoBase):
    """
    Catálogo de tipos de citas bibliográficas.

    Cada tipo de cita incluye un color asociado y un peso métrico
    utilizado en el cálculo de impacto.
    
    Attributes:
        color_interfaz (str): Código hexadecimal del color.
        peso_metrico (Decimal): Factor de ponderación (0–9.99).
    """
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
    """
    Catálogo de formatos de archivo aceptados en el sistema.

    Define las extensiones, tipos MIME y límites de tamaño máximo
    para los archivos que se pueden subir.

    Attributes:
        extension (str): Extensión del archivo sin punto inicial.
        mime_type (str): Tipo MIME (por ejemplo, 'application/pdf').
        tamaño_maximo_mb (int): Tamaño máximo permitido en MB.
    """
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
        """
        Normaliza la extensión antes de guardar.

        Elimina puntos y convierte a minúsculas.
        """
        if self.extension:
            self.extension = self.extension.strip().lower().replace(".", "")


class AreaConocimiento(CatalogoBase):
    """
    Catálogo jerárquico de áreas del conocimiento.

    Permite definir una estructura padre-hijo para representar
    la jerarquía entre áreas científicas o académicas.

    Attributes:
        area_padre (AreaConocimiento): Área de conocimiento superior.
        codigo_externo (str): Código externo (por ejemplo, CONACYT o UNESCO).
    """
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
        """
        Calcula el nivel jerárquico del área.

        Returns:
            int: Nivel en la jerarquía (0 para áreas raíz).
        """
        nivel, area_actual = 0, self.area_padre
        while area_actual is not None:
            nivel += 1
            area_actual = area_actual.area_padre
        return nivel


class Institucion(CatalogoBase):
    """
    Catálogo de instituciones académicas y de investigación.

    Incluye universidades, centros de investigación y organismos públicos
    o privados, asociándolos a un país.

    Attributes:
        tipo_institucion (str): Tipo de institución (por ejemplo, 'UNIVERSIDAD').
        pais (Pais): País al que pertenece la institución.
        sitio_web (str): URL del sitio web institucional.
    """
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
    """
    Catálogo de fuentes de financiamiento para investigación.

    Define las posibles fuentes de apoyo económico para proyectos
    académicos, empresariales o gubernamentales.

    Attributes:
        tipo_fuente (str): Tipo de fuente (Gubernamental, Internacional, etc.).
        monto_maximo (Decimal): Monto máximo típico en pesos mexicanos.
        vigente (bool): Indica si la fuente está disponible actualmente.
    """
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
