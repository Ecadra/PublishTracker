# journals/models.py
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime
from core.models import Pais
import os
from django.utils.text import slugify


def revista_file_path(instance, filename):
    """
    Generar la ruta y el nombre del archivo de revista.
    Pasos:
    1. Obtener edición y revista
    2. Normalizar y truncar identificadores
    3. Extraer extensión original
    4. Construir nombre de archivo final
    5. Construir ruta final por año y revista
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
    nombre = models.CharField(max_length=200, db_index=True, verbose_name="Nombre")
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, verbose_name="País")
    direccion = models.TextField(blank=True, null=True, verbose_name="Dirección")

    class Meta:
        managed = True
        verbose_name = "Editorial"
        verbose_name_plural = "Editoriales"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        """
        Normalizar y guardar la editorial.
        Pasos:
        1. Limpiar y capitalizar nombre
        2. Delegar guardado al método base
        """
        # 1. Limpiar y capitalizar nombre
        if self.nombre:
            self.nombre = self.nombre.strip().title()

        # 2. Delegar guardado al método base
        super().save(*args, **kwargs)

    @property
    def nombre_completo(self):
        """
        Construir nombre con país.
        Pasos:
        1. Unir nombre y país
        2. Retornar representación legible
        """
        # 1. Unir nombre y país
        # 2. Retornar representación legible
        return f"{self.nombre} - {self.pais.nombre}"


class CategoriaRevista(models.Model):
    nombre = models.CharField(max_length=100, unique=True, db_index=True, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        managed = True
        verbose_name = "Categoría de Revista"
        verbose_name_plural = "Categorías de Revistas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class AmbitoRevista(models.Model):
    nombre = models.CharField(max_length=100, unique=True, db_index=True, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        managed = True
        verbose_name = "Ámbito de Revista"
        verbose_name_plural = "Ámbitos de Revistas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Revista(models.Model):
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
        return self.nombre

    def save(self, *args, **kwargs):
        """
        Normalizar y guardar la revista.
        Pasos:
        1. Limpiar y capitalizar nombre
        2. Delegar guardado al método base
        """
        # 1. Limpiar y capitalizar nombre
        if self.nombre:
            self.nombre = self.nombre.strip().title()

        # 2. Delegar guardado al método base
        super().save(*args, **kwargs)

    @property
    def tiene_issn(self):
        """
        Verificar presencia de ISSN.
        Pasos:
        1. Revisar campos de ISSN
        2. Retornar booleano de existencia
        """
        # 1. Revisar campos de ISSN
        # 2. Retornar booleano de existencia
        return bool(self.issn_impreso or self.issn_electronico)

    @property
    def issn_principal(self):
        """
        Determinar ISSN principal.
        Pasos:
        1. Priorizar ISSN electrónico
        2. Usar ISSN impreso como alternativa
        3. Devolver marcador si no existe
        """
        # 1. Priorizar ISSN electrónico
        # 2. Usar ISSN impreso como alternativa
        # 3. Devolver marcador si no existe
        return self.issn_electronico or self.issn_impreso or "Sin ISSN"


class EdicionRevista(models.Model):
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
        return f"{self.revista.nombre} - {self.anio} {f'Vol.{self.volumen}' if self.volumen else ''} {f'No.{self.numero}' if self.numero else ''}".strip()

    @property
    def nombre_corto(self):
        """
        Construir nombre corto de edición.
        Pasos:
        1. Tomar volumen y número (o guiones)
        2. Componer cadena con año
        """
        # 1. Tomar volumen y número (o guiones)
        vol = self.volumen or '-'
        num = self.numero or '-'

        # 2. Componer cadena con año
        return f"Vol.{vol} No.{num} ({self.anio})"


class TipoArchivoRevista(models.Model):
    tipo = models.CharField(max_length=50, unique=True, db_index=True, verbose_name="Tipo")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        managed = True
        verbose_name = "Tipo de Archivo de Revista"
        verbose_name_plural = "Tipos de Archivos de Revistas"
        ordering = ['tipo']

    def __str__(self):
        return self.tipo


class ArchivoRevista(models.Model):
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
        return f"{self.nombre_archivo} - {self.edicion}"

    @property
    def extension(self):
        """
        Obtener extensión del archivo.
        Pasos:
        1. Verificar presencia de punto
        2. Extraer y normalizar extensión
        """
        # 1. Verificar presencia de punto
        # 2. Extraer y normalizar extensión
        return self.nombre_archivo.split('.')[-1].lower() if '.' in self.nombre_archivo else ''

    @property
    def tamano_legible(self):
        """
        Formatear tamaño del archivo en unidades legibles.
        Pasos:
        1. Obtener tamaño en bytes
        2. Iterar unidades hasta ajustar escala
        3. Retornar cadena formateada
        4. Manejar errores devolviendo marcador
        """
        try:
            # 1. Obtener tamaño en bytes
            size = self.archivo.size

            # 2. Iterar unidades hasta ajustar escala
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    # 3. Retornar cadena formateada
                    return f"{size:.1f} {unit}"
                size /= 1024.0

            return f"{size:.1f} TB"
        except Exception:
            # 4. Manejar errores devolviendo marcador
            return "Tamaño desconocido"
