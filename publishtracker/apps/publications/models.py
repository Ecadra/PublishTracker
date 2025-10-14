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
    """Genera la ruta y el nombre para los archivos del paper."""
    paper = instance.paper
    edicion = paper.edicion
    revista = edicion.revista

    # Limpia los nombres
    tipo_slug = slugify(instance.tipo_archivo.tipo)
    revista_slug = slugify(revista.nombre)[:15]
    paper_slug = slugify(paper.titulo)[:20] # Trunca a 20 caracteres

    # Obtiene la extensión
    ext = os.path.splitext(filename)[1]

    # Construye el nuevo nombre de archivo: Tipo_año_revista_articulo.ext
    new_filename = f"{tipo_slug}_{edicion.anio}_{revista_slug}_{paper_slug}{ext}"

    # Construye la ruta de la carpeta: Año/IDRevista/IDPaper/
    path = os.path.join(str(edicion.anio), str(revista.id), str(paper.id))

    return os.path.join(path, new_filename)
class Paper(models.Model):
    """Modelo principal para papers/artículos científicos"""

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
    proposito = models.TextField(blank = True, null = True, verbose_name="Proposito")
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
        managed=True
        verbose_name = "Paper"
        verbose_name_plural = "Papers"
        ordering = ['-anio_publicacion', '-fecha_creacion']

    def __str__(self):
        titulo_corto = self.titulo[:50] + "..." if len(self.titulo) > 50 else self.titulo
        return f"{titulo_corto} ({self.anio_publicacion})"

    def save(self, *args, **kwargs):
        """Normalización antes de guardar"""
        if self.titulo:
            self.titulo = self.titulo.strip()
        if self.doi:
            clean_doi = self.doi.strip()
            if clean_doi.startswith('https://doi.org/'):
                clean_doi = clean_doi.replace('https://doi.org/', '')
            elif clean_doi.startswith('http://dx.doi.org/'):
                clean_doi = clean_doi.replace('http://dx.doi.org/', '')
            elif clean_doi.startswith('doi:'):
                clean_doi = clean_doi.replace('doi:', '')
            self.doi = clean_doi
        super().save(*args, **kwargs)

    @property
    def doi_url(self):
        return f"https://doi.org/{self.doi}" if self.doi else None

    @property
    def titulo_corto(self):
        return self.titulo[:100] + "..." if len(self.titulo) > 100 else self.titulo

    @property
    def rango_paginas(self):
        if self.pagina_inicio and self.pagina_fin:
            return f"{self.pagina_inicio}-{self.pagina_fin}"
        elif self.pagina_inicio:
            return str(self.pagina_inicio)
        return "Sin páginas"

    @property
    def numero_paginas(self):
        if self.pagina_inicio and self.pagina_fin and self.pagina_fin >= self.pagina_inicio:
            return self.pagina_fin - self.pagina_inicio + 1
        return None

    @property
    def tiene_apoyo_institucional(self):
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
    tipo_cita=models.CharField(max_length=100, verbose_name="Tipo de Cita")
    texto_cita = models.TextField(verbose_name="Texto de la Cita")
class TipoArchivoPaper(models.Model):
    """Define los tipos de archivos que se pueden asociar a un paper."""
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
    """Tabla intermedia que asocia un archivo físico con un Paper y su tipo."""
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
        # Asegura que no se pueda subir el mismo tipo de archivo dos veces para el mismo paper
        unique_together = ['paper', 'tipo_archivo']
    
    def __str__(self):
        return f"{self.nombre_archivo} ({self.tipo_archivo.tipo}) - {self.paper.titulo_corto}"

    @property
    def extension(self):
        return self.nombre_archivo.split('.')[-1].lower() if '.' in self.nombre_archivo else ''