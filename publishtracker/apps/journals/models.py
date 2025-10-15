from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime
from core.models import Pais
from django.utils.text import slugify
import os


def revista_file_path(instance, filename):
    """
    Genera dinámicamente la ruta y el nombre de archivo para las revistas.

    Crea un nombre de archivo basado en el tipo de archivo, año de publicación
    y nombre de la revista, asegurando una estructura organizada de almacenamiento.

    Args:
        instance (ArchivoRevista): Instancia actual del archivo asociado.
        filename (str): Nombre original del archivo subido.

    Returns:
        str: Ruta relativa donde se guardará el archivo.
    """
    # 1. Obtener edición y revista
    edicion = instance.edicion
    revista = edicion.revista

    # 2. Normalizar y truncar identificadores
    tipo_slug = slugify(instance.tipo_archivo.tipo)
    revista_slug = slugify(revista.nombre)[:15]

    # 3. Extraer extensión original
    ext = os.path.splitext(filename)[1]

    # 4. Construir nombre de archivo final
    new_filename = f"{tipo_slug}_{edicion.anio}_{revista_slug}{ext}"

    # 5. Construir ruta final por año y revista
    path = os.path.join(str(edicion.anio), str(revista.id))
    return os.path.join(path, new_filename)


class Editorial(models.Model):
    """
    Representa una editorial asociada a publicaciones académicas.

    Attributes:
        nombre (str): Nombre de la editorial.
        pais (Pais): País de origen de la editorial.
        direccion (str): Dirección opcional de la sede editorial.
    """
    nombre = models.CharField(max_length=200, db_index=True, verbose_name="Nombre")
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, verbose_name="País")
    direccion = models.TextField(blank=True, null=True, verbose_name="Dirección")

    class Meta:
        managed = True
        verbose_name = "Editorial"
        verbose_name_plural = "Editoriales"
        ordering = ['nombre']

    def __str__(self):
        """Devuelve el nombre de la editorial."""
        return self.nombre

    def save(self, *args, **kwargs):
        """
        Normaliza el nombre de la editorial antes de guardar.

        Capitaliza el texto y elimina espacios innecesarios.
        """
        if self.nombre:
            self.nombre = self.nombre.strip().title()
        super().save(*args, **kwargs)

    @property
    def nombre_completo(self):
        """
        Devuelve el nombre completo de la editorial con su país.

        Returns:
            str: Formato “Nombre - País”.
        """
        return f"{self.nombre} - {self.pais.nombre}"


class CategoriaRevista(models.Model):
    """
    Define categorías temáticas de revistas.

    Attributes:
        nombre (str): Nombre único de la categoría.
        descripcion (str): Descripción opcional.
    """
    nombre = models.CharField(max_length=100, unique=True, db_index=True, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        managed = True
        verbose_name = "Categoría de Revista"
        verbose_name_plural = "Categorías de Revistas"
        ordering = ['nombre']

    def __str__(self):
        """Devuelve el nombre de la categoría."""
        return self.nombre


class AmbitoRevista(models.Model):
    """
    Representa los ámbitos o áreas de alcance de una revista.

    Attributes:
        nombre (str): Nombre único del ámbito.
        descripcion (str): Descripción opcional.
    """
    nombre = models.CharField(max_length=100, unique=True, db_index=True, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        managed = True
        verbose_name = "Ámbito de Revista"
        verbose_name_plural = "Ámbitos de Revistas"
        ordering = ['nombre']

    def __str__(self):
        """Devuelve el nombre del ámbito."""
        return self.nombre


class Revista(models.Model):
    """
    Modelo que representa una revista académica.

    Incluye metadatos como ISSN, país, editorial, categoría y
    un indicador de si está dirigida a cuerpos académicos.

    Attributes:
        nombre (str): Nombre de la revista.
        issn_impreso (str): ISSN de versión impresa.
        issn_electronico (str): ISSN de versión electrónica.
        factor_impacto (Decimal): Valor numérico del impacto.
        editorial (Editorial): Editorial asociada.
        url (str): Enlace a la página oficial de la revista.
        pais_publicacion (Pais): País donde se publica.
        categoria (CategoriaRevista): Categoría temática.
        ambito (AmbitoRevista): Ámbito o área de especialización.
        dirigido_cuerpo_academico (bool): Indica si está dirigida a cuerpos académicos.
    """
    nombre = models.CharField(max_length=300, db_index=True, verbose_name="Nombre")
    issn_impreso = models.CharField(max_length=20, blank=True, null=True, verbose_name="ISSN Impreso")
    issn_electronico = models.CharField(max_length=20, blank=True, null=True, verbose_name="ISSN Electrónico")
    factor_impacto = models.DecimalField(
        max_digits=7,
        decimal_places=3,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name="Factor de Impacto"
    )
    editorial = models.ForeignKey(Editorial, on_delete=models.CASCADE, verbose_name="Editorial")
    url = models.URLField(blank=True, null=True, verbose_name="URL")
    pais_publicacion = models.ForeignKey(Pais, on_delete=models.CASCADE, verbose_name="País de Publicación")
    categoria = models.ForeignKey(CategoriaRevista, on_delete=models.CASCADE, verbose_name="Categoría")
    ambito = models.ForeignKey(AmbitoRevista, on_delete=models.CASCADE, verbose_name="Ámbito")
    dirigido_cuerpo_academico = models.BooleanField(default=False, verbose_name="Dirigido a Cuerpo Académico")

    class Meta:
        managed = True
        verbose_name = "Revista"
        verbose_name_plural = "Revistas"
        ordering = ['nombre']

    def __str__(self):
        """Devuelve el nombre de la revista."""
        return self.nombre

    def save(self, *args, **kwargs):
        """
        Normaliza el nombre de la revista antes de guardar.
        """
        if self.nombre:
            self.nombre = self.nombre.strip().title()
        super().save(*args, **kwargs)

    @property
    def tiene_issn(self):
        """
        Indica si la revista cuenta con al menos un ISSN.

        Returns:
            bool: True si tiene ISSN impreso o electrónico.
        """
        return bool(self.issn_impreso or self.issn_electronico)

    @property
    def issn_principal(self):
        """
        Devuelve el ISSN principal de la revista.

        Prioriza el ISSN electrónico sobre el impreso.

        Returns:
            str: ISSN principal o "Sin ISSN" si no existe.
        """
        return self.issn_electronico or self.issn_impreso or "Sin ISSN"


class EdicionRevista(models.Model):
    """
    Representa una edición específica de una revista.

    Attributes:
        revista (Revista): Revista asociada.
        anio (int): Año de publicación.
        volumen (str): Número de volumen (opcional).
        numero (str): Número de edición (opcional).
        indice_revista (str): Índice o clasificación de la edición.
    """
    revista = models.ForeignKey(Revista, on_delete=models.CASCADE, verbose_name="Revista")
    anio = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(datetime.now().year + 5)
        ],
        verbose_name="Año"
    )
    volumen = models.CharField(max_length=20, blank=True, null=True, verbose_name="Volumen")
    numero = models.CharField(max_length=20, blank=True, null=True, verbose_name="Número")
    indice_revista = models.CharField(max_length=100, blank=True, null=True, verbose_name="Índice de Revista")

    class Meta:
        managed = True
        verbose_name = "Edición de Revista"
        verbose_name_plural = "Ediciones de Revistas"
        ordering = ['-anio', 'revista__nombre']
        unique_together = ['revista', 'anio', 'volumen', 'numero']

    def __str__(self):
        """Devuelve una representación legible de la edición."""
        return f"{self.revista.nombre} - {self.anio} {f'Vol.{self.volumen}' if self.volumen else ''} {f'No.{self.numero}' if self.numero else ''}".strip()

    @property
    def nombre_corto(self):
        """
        Devuelve un nombre abreviado de la edición.

        Returns:
            str: Formato “Vol.X No.Y (Año)”.
        """
        vol = self.volumen or '-'
        num = self.numero or '-'
        return f"Vol.{vol} No.{num} ({self.anio})"


class TipoArchivoRevista(models.Model):
    """
    Define los tipos de archivos asociados a una revista.

    Attributes:
        tipo (str): Nombre del tipo de archivo (ej. "PDF", "Portada").
        descripcion (str): Descripción opcional del tipo.
    """
    tipo = models.CharField(max_length=50, unique=True, db_index=True, verbose_name="Tipo")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        managed = True
        verbose_name = "Tipo de Archivo de Revista"
        verbose_name_plural = "Tipos de Archivos de Revistas"
        ordering = ['tipo']

    def __str__(self):
        """Devuelve el nombre del tipo de archivo."""
        return self.tipo


class ArchivoRevista(models.Model):
    """
    Representa un archivo vinculado a una edición de revista.

    Attributes:
        edicion (EdicionRevista): Edición a la que pertenece el archivo.
        tipo_archivo (TipoArchivoRevista): Tipo de archivo asociado.
        nombre_archivo (str): Nombre del archivo almacenado.
        archivo (FileField): Archivo físico subido al servidor.
        fecha_subida (datetime): Fecha de carga.
    """
    edicion = models.ForeignKey(EdicionRevista, on_delete=models.CASCADE, verbose_name="Edición")
    tipo_archivo = models.ForeignKey(TipoArchivoRevista, on_delete=models.CASCADE, verbose_name="Tipo de Archivo")
    nombre_archivo = models.CharField(max_length=255, verbose_name="Nombre del Archivo")
    archivo = models.FileField(upload_to=revista_file_path, verbose_name="Archivo")
    fecha_subida = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Subida")

    class Meta:
        managed = True
        verbose_name = "Archivo de Revista"
        verbose_name_plural = "Archivos de Revistas"
        ordering = ['-fecha_subida']

    def __str__(self):
        """Devuelve el nombre del archivo con su edición."""
        return f"{self.nombre_archivo} - {self.edicion}"

    @property
    def extension(self):
        """
        Devuelve la extensión del archivo.

        Returns:
            str: Extensión en minúsculas (sin punto).
        """
        return self.nombre_archivo.split('.')[-1].lower() if '.' in self.nombre_archivo else ''

    @property
    def tamano_legible(self):
        """
        Convierte el tamaño del archivo a formato legible (B, KB, MB, GB).

        Returns:
            str: Tamaño del archivo formateado o “Tamaño desconocido”.
        """
        try:
            size = self.archivo.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except Exception:
            return "Tamaño desconocido"
