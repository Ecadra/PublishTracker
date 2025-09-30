# publications/models.py
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime
from core.models import EstatusPublicacion, ProgramaSeciti, EjeSecithi
from journals.models import EdicionRevista


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

    # ---- PROPIEDADES ÚTILES ----
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