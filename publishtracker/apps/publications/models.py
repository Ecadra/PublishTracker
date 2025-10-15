# publications/models.py
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime
from core.models import EstatusPublicacion, ProgramaSeciti, EjeSecithi
from journals.models import EdicionRevista
import os
from django.utils.text import slugify


def paper_file_path(instance, filename):
    """
    Generar la ruta y el nombre del archivo de paper.
    Pasos:
    1. Obtener referencias a paper, edición y revista
    2. Normalizar y truncar identificadores
    3. Extraer extensión del nombre original
    4. Construir nombre de archivo final
    5. Construir ruta final Año/IDRevista/IDPaper
    """
    # 1. Obtener referencias a paper, edición y revista
    paper = instance.paper
    edicion = paper.edicion
    revista = edicion.revista

    # 2. Normalizar y truncar identificadores
    tipo_slug = slugify(instance.tipo_archivo.tipo)
    revista_slug = slugify(revista.nombre)[:15]
    paper_slug = slugify(paper.titulo)[:20]

    # 3. Extraer extensión del nombre original
    ext = os.path.splitext(filename)[1]

    # 4. Construir nombre de archivo final
    new_filename = f"{tipo_slug}_{edicion.anio}_{revista_slug}_{paper_slug}{ext}"

    # 5. Construir ruta final Año/IDRevista/IDPaper
    path = os.path.join(str(edicion.anio), str(revista.id), str(paper.id))
    return os.path.join(path, new_filename)


class Paper(models.Model):
    edicion = models.ForeignKey(
        EdicionRevista,
        on_delete=models.CASCADE,
        verbose_name="Edición de Revista"
    )
    doi = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        db_index=True,
        verbose_name="DOI",
        help_text="Digital Object Identifier"
    )
    titulo = models.CharField(
        max_length=500,
        db_index=True,
        verbose_name="Título"
    )
    anio_publicacion = models.IntegerField(
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(datetime.now().year + 5)
        ],
        verbose_name="Año de Publicación"
    )
    recibio_apoyo_seciti = models.BooleanField(
        default=False,
        verbose_name="Recibió Apoyo SECITI"
    )
    programa = models.ForeignKey(
        ProgramaSeciti,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Programa SECITI"
    )
    estatus_publicacion = models.ForeignKey(
        EstatusPublicacion,
        on_delete=models.CASCADE,
        verbose_name="Estatus de Publicación"
    )
    proposito = models.TextField(blank=True, null=True, verbose_name="Proposito")
    objetivo = models.TextField(blank=True, null=True, verbose_name="Objetivo")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    abstract = models.TextField(blank=True, null=True, verbose_name="Abstract")
    url_cita = models.URLField(blank=True, null=True, verbose_name="URL de Cita")
    total_citas = models.PositiveIntegerField(
        default=0,
        verbose_name="Total de Citas"
    )
    eje_secithi = models.ForeignKey(
        EjeSecithi,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Eje SECITHI"
    )
    pagina_inicio = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Página Inicio"
    )
    pagina_fin = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Página Fin"
    )
    referencia_apa = models.TextField(blank=True, null=True, verbose_name="Referencia APA")
    fecha_creacion = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    # Relación many-to-many con autores a través del modelo intermedio
    autores = models.ManyToManyField(
        'authors.Autor',
        through='authors.PaperAutor',
        verbose_name="Autores"
    )

    class Meta:
        managed = True
        verbose_name = "Paper"
        verbose_name_plural = "Papers"
        ordering = ['-anio_publicacion', '-fecha_creacion']

    def __str__(self):
        titulo_corto = self.titulo[:50] + "..." if len(self.titulo) > 50 else self.titulo
        return f"{titulo_corto} ({self.anio_publicacion})"

    def save(self, *args, **kwargs):
        """
        Normalizar campos y guardar el paper.
        Pasos:
        1. Limpiar espacios del título
        2. Limpiar y estandarizar el DOI (si existe)
        3. Delegar el guardado al método base
        """
        # 1. Limpiar espacios del título
        if self.titulo:
            self.titulo = self.titulo.strip()

        # 2. Limpiar y estandarizar el DOI (si existe)
        if self.doi:
            clean_doi = self.doi.strip()
            if clean_doi.startswith('https://doi.org/'):
                clean_doi = clean_doi.replace('https://doi.org/', '')
            elif clean_doi.startswith('http://dx.doi.org/'):
                clean_doi = clean_doi.replace('http://dx.doi.org/', '')
            elif clean_doi.startswith('doi:'):
                clean_doi = clean_doi.replace('doi:', '')
            self.doi = clean_doi

        # 3. Delegar el guardado al método base
        super().save(*args, **kwargs)

    @property
    def doi_url(self):
        """
        Construir URL pública del DOI.
        Pasos:
        1. Verificar existencia de DOI
        2. Componer y retornar la URL
        """
        # 1. Verificar existencia de DOI
        # 2. Componer y retornar la URL
        return f"https://doi.org/{self.doi}" if self.doi else None

    @property
    def titulo_corto(self):
        """
        Obtener versión corta del título.
        Pasos:
        1. Evaluar longitud del título
        2. Truncar y agregar elipsis si aplica
        3. Retornar la cadena resultante
        """
        # 1. Evaluar longitud del título
        # 2. Truncar y agregar elipsis si aplica
        # 3. Retornar la cadena resultante
        return self.titulo[:100] + "..." if len(self.titulo) > 100 else self.titulo

    @property
    def rango_paginas(self):
        """
        Construir representación del rango de páginas.
        Pasos:
        1. Verificar inicio y fin
        2. Formatear rango o único valor
        3. Retornar marcador si no hay datos
        """
        # 1. Verificar inicio y fin
        if self.pagina_inicio and self.pagina_fin:
            # 2. Formatear rango o único valor
            return f"{self.pagina_inicio}-{self.pagina_fin}"
        elif self.pagina_inicio:
            return str(self.pagina_inicio)
        # 3. Retornar marcador si no hay datos
        return "Sin páginas"

    @property
    def numero_paginas(self):
        """
        Calcular el número de páginas.
        Pasos:
        1. Verificar que inicio y fin existan y sean válidos
        2. Calcular diferencia inclusiva
        3. Retornar None si no aplica
        """
        # 1. Verificar que inicio y fin existan y sean válidos
        if self.pagina_inicio and self.pagina_fin and self.pagina_fin >= self.pagina_inicio:
            # 2. Calcular diferencia inclusiva
            return self.pagina_fin - self.pagina_inicio + 1
        # 3. Retornar None si no aplica
        return None

    @property
    def tiene_apoyo_institucional(self):
        """
        Verificar apoyo institucional SECITI.
        Pasos:
        1. Comprobar bandera de apoyo
        2. Verificar existencia de programa asociado
        3. Retornar booleano resultante
        """
        # 1. Comprobar bandera de apoyo
        # 2. Verificar existencia de programa asociado
        # 3. Retornar booleano resultante
        return self.recibio_apoyo_seciti and self.programa is not None


class PalabraClave(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Palabra Clave")


class PaperPalabraClave(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    palabra_clave = models.ForeignKey(PalabraClave, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('paper', 'palabra_clave')
        verbose_name = "Relación Paper-Palabra Clave"
        verbose_name_plural = "Relaciones Paper-Palabra Clave"


class Cita(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='citas')
    tipo_cita = models.CharField(max_length=100, verbose_name="Tipo de Cita")
    texto_cita = models.TextField(verbose_name="Texto de la Cita")


class TipoArchivoPaper(models.Model):
    tipo = models.CharField(max_length=100, unique=True, db_index=True, verbose_name="Tipo de Archivo")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        managed = True
        verbose_name = "Tipo de Archivo de Paper"
        verbose_name_plural = "Tipos de Archivos de Paper"
        ordering = ['tipo']

    def __str__(self):
        return self.tipo


class ArchivoPaper(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='archivos', verbose_name="Paper")
    tipo_archivo = models.ForeignKey(TipoArchivoPaper, on_delete=models.CASCADE, verbose_name="Tipo de Archivo")
    nombre_archivo = models.CharField(max_length=255, verbose_name="Nombre del Archivo")
    archivo = models.FileField(upload_to=paper_file_path, verbose_name="Archivo")
    fecha_subida = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Subida")

    class Meta:
        managed = True
        verbose_name = "Archivo de Paper"
        verbose_name_plural = "Archivos de Papers"
        ordering = ['-fecha_subida']
        unique_together = ['paper', 'tipo_archivo']

    def __str__(self):
        return f"{self.nombre_archivo} ({self.tipo_archivo.tipo}) - {self.paper.titulo_corto}"

    @property
    def extension(self):
        """
        Obtener extensión del archivo.
        Pasos:
        1. Verificar presencia de punto en el nombre
        2. Extraer y normalizar la extensión
        3. Retornar cadena vacía si no hay extensión
        """
        # 1. Verificar presencia de punto en el nombre
        # 2. Extraer y normalizar la extensión
        return self.nombre_archivo.split('.')[-1].lower() if '.' in self.nombre_archivo else ''
