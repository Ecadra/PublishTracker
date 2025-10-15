from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime
from core.models import EstatusPublicacion, ProgramaSeciti, EjeSecithi
from journals.models import EdicionRevista
from authors.models import Autor, RolAutor
from django.utils.text import slugify
import os


def paper_file_path(instance, filename):
    """
    Genera dinámicamente la ruta y el nombre de archivo para un paper.

    La estructura del nombre incluye el tipo de archivo, año de la edición,
    nombre de la revista y título del paper, organizados jerárquicamente
    por año y revista.

    Args:
        instance (ArchivoPaper): Instancia actual del archivo.
        filename (str): Nombre original del archivo.

    Returns:
        str: Ruta relativa donde se guardará el archivo.
    """
    paper = instance.paper
    edicion = paper.edicion
    revista = edicion.revista

    tipo_slug = slugify(instance.tipo_archivo.tipo)
    revista_slug = slugify(revista.nombre)[:15]
    paper_slug = slugify(paper.titulo)[:20]

    ext = os.path.splitext(filename)[1]
    new_filename = f"{tipo_slug}_{edicion.anio}_{revista_slug}_{paper_slug}{ext}"
    path = os.path.join(str(edicion.anio), str(revista.id), str(paper.id))
    return os.path.join(path, new_filename)


class Paper(models.Model):
    """
    Representa un artículo científico (paper) publicado en una revista.

    Incluye metadatos bibliográficos, DOI, autores, número de páginas,
    vínculos con programas de apoyo y eje temático SECITHI.

    Attributes:
        edicion (EdicionRevista): Edición de revista en la que se publica.
        doi (str): Digital Object Identifier único.
        titulo (str): Título del paper.
        anio_publicacion (int): Año de publicación.
        recibio_apoyo_seciti (bool): Indica si recibió apoyo de SECITI.
        programa (ProgramaSeciti): Programa de apoyo asociado.
        estatus_publicacion (EstatusPublicacion): Estatus actual del paper.
        proposito (str): Propósito del estudio.
        objetivo (str): Objetivo principal.
        descripcion (str): Descripción general del paper.
        abstract (str): Resumen en inglés.
        url_cita (str): URL de referencia o cita.
        total_citas (int): Número total de citas registradas.
        eje_secithi (EjeSecithi): Eje de investigación asociado.
        pagina_inicio (int): Página inicial en la revista.
        pagina_fin (int): Página final en la revista.
        referencia_apa (str): Cita completa en formato APA.
        fecha_creacion (datetime): Fecha de registro.
        fecha_actualizacion (datetime): Fecha de última modificación.
        autores (ManyToManyField): Autores asociados al paper.
    """
    edicion = models.ForeignKey(EdicionRevista, on_delete=models.CASCADE, verbose_name="Edición de Revista")
    doi = models.CharField(max_length=100, unique=True, blank=True, null=True, db_index=True,
                           verbose_name="DOI", help_text="Digital Object Identifier")
    titulo = models.CharField(max_length=500, db_index=True, verbose_name="Título")
    anio_publicacion = models.IntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(datetime.now().year + 5)],
        verbose_name="Año de Publicación"
    )
    recibio_apoyo_seciti = models.BooleanField(default=False, verbose_name="Recibió Apoyo SECITI")
    programa = models.ForeignKey(ProgramaSeciti, on_delete=models.SET_NULL, blank=True, null=True,
                                 verbose_name="Programa SECITI")
    estatus_publicacion = models.ForeignKey(EstatusPublicacion, on_delete=models.CASCADE,
                                            verbose_name="Estatus de Publicación")
    proposito = models.TextField(blank=True, null=True, verbose_name="Proposito")
    objetivo = models.TextField(blank=True, null=True, verbose_name="Objetivo")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    abstract = models.TextField(blank=True, null=True, verbose_name="Abstract")
    url_cita = models.URLField(blank=True, null=True, verbose_name="URL de Cita")
    total_citas = models.PositiveIntegerField(default=0, verbose_name="Total de Citas")
    eje_secithi = models.ForeignKey(EjeSecithi, on_delete=models.SET_NULL, blank=True, null=True,
                                    verbose_name="Eje SECITHI")
    pagina_inicio = models.PositiveIntegerField(blank=True, null=True, verbose_name="Página Inicio")
    pagina_fin = models.PositiveIntegerField(blank=True, null=True, verbose_name="Página Fin")
    referencia_apa = models.TextField(blank=True, null=True, verbose_name="Referencia APA")
    fecha_creacion = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    autores = models.ManyToManyField(Autor, through='PaperAutor', verbose_name="Autores")

    class Meta:
        managed = True
        verbose_name = "Paper"
        verbose_name_plural = "Papers"
        ordering = ['-anio_publicacion', '-fecha_creacion']

    def __str__(self):
        """Devuelve el título abreviado del paper con su año."""
        titulo_corto = self.titulo[:50] + "..." if len(self.titulo) > 50 else self.titulo
        return f"{titulo_corto} ({self.anio_publicacion})"

    def save(self, *args, **kwargs):
        """
        Normaliza los campos antes de guardar el paper.

        Limpia espacios en el título y estandariza el formato del DOI.
        """
        if self.titulo:
            self.titulo = self.titulo.strip()

        if self.doi:
            clean_doi = self.doi.strip()
            for prefix in ('https://doi.org/', 'http://dx.doi.org/', 'doi:'):
                if clean_doi.startswith(prefix):
                    clean_doi = clean_doi.replace(prefix, '')
            self.doi = clean_doi

        super().save(*args, **kwargs)

    @property
    def doi_url(self):
        """
        Devuelve la URL completa del DOI.

        Returns:
            str | None: URL pública del DOI o None si no existe.
        """
        return f"https://doi.org/{self.doi}" if self.doi else None

    @property
    def titulo_corto(self):
        """
        Devuelve una versión abreviada del título.

        Returns:
            str: Primeros 100 caracteres del título seguidos de “...” si aplica.
        """
        return self.titulo[:100] + "..." if len(self.titulo) > 100 else self.titulo

    @property
    def rango_paginas(self):
        """
        Construye la representación textual del rango de páginas.

        Returns:
            str: Rango “inicio-fin”, un solo número o “Sin páginas”.
        """
        if self.pagina_inicio and self.pagina_fin:
            return f"{self.pagina_inicio}-{self.pagina_fin}"
        elif self.pagina_inicio:
            return str(self.pagina_inicio)
        return "Sin páginas"

    @property
    def numero_paginas(self):
        """
        Calcula el número total de páginas del paper.

        Returns:
            int | None: Cantidad de páginas si los datos son válidos.
        """
        if self.pagina_inicio and self.pagina_fin and self.pagina_fin >= self.pagina_inicio:
            return self.pagina_fin - self.pagina_inicio + 1
        return None

    @property
    def tiene_apoyo_institucional(self):
        """
        Indica si el paper tiene apoyo institucional SECITI.

        Returns:
            bool: True si recibió apoyo SECITI y tiene un programa asociado.
        """
        return self.recibio_apoyo_seciti and self.programa is not None


class PalabraClave(models.Model):
    """
    Representa una palabra clave utilizada para clasificar papers.

    Attributes:
        nombre (str): Texto único de la palabra clave.
    """
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Palabra Clave")


class PaperPalabraClave(models.Model):
    """
    Relación intermedia entre Paper y PalabraClave.

    Asocia múltiples palabras clave a un mismo paper.
    """
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    palabra_clave = models.ForeignKey(PalabraClave, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('paper', 'palabra_clave')
        verbose_name = "Relación Paper-Palabra Clave"
        verbose_name_plural = "Relaciones Paper-Palabra Clave"


class Cita(models.Model):
    """
    Representa una cita asociada a un paper.

    Attributes:
        paper (Paper): Paper citado.
        tipo_cita (str): Tipo o fuente de la cita.
        texto_cita (str): Texto completo de la cita.
    """
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='citas')
    tipo_cita = models.CharField(max_length=100, verbose_name="Tipo de Cita")
    texto_cita = models.TextField(verbose_name="Texto de la Cita")


class TipoArchivoPaper(models.Model):
    """
    Catálogo de tipos de archivos asociados a papers.

    Attributes:
        tipo (str): Nombre del tipo de archivo (ej. 'PDF', 'Portada').
        descripcion (str): Descripción opcional del tipo.
    """
    tipo = models.CharField(max_length=100, unique=True, db_index=True, verbose_name="Tipo de Archivo")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        managed = True
        verbose_name = "Tipo de Archivo de Paper"
        verbose_name_plural = "Tipos de Archivos de Paper"
        ordering = ['tipo']

    def __str__(self):
        """Devuelve el nombre del tipo de archivo."""
        return self.tipo


class ArchivoPaper(models.Model):
    """
    Representa un archivo asociado a un paper.

    Attributes:
        paper (Paper): Paper al que pertenece.
        tipo_archivo (TipoArchivoPaper): Tipo del archivo.
        nombre_archivo (str): Nombre original o descriptivo del archivo.
        archivo (FileField): Archivo físico almacenado.
        fecha_subida (datetime): Fecha en que se subió el archivo.
    """
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
        """Devuelve el nombre del archivo junto con el tipo y el título del paper."""
        return f"{self.nombre_archivo} ({self.tipo_archivo.tipo}) - {self.paper.titulo_corto}"

    @property
    def extension(self):
        """
        Devuelve la extensión del archivo.

        Returns:
            str: Extensión del archivo o cadena vacía si no aplica.
        """
        return self.nombre_archivo.split('.')[-1].lower() if '.' in self.nombre_archivo else ''


class PaperAutor(models.Model):
    """
    Relación intermedia entre Paper y Autor, con información de orden y rol.

    Attributes:
        paper (Paper): Paper asociado.
        autor (Autor): Autor participante.
        orden_autor (int): Posición del autor (1 = primer autor).
        rol_autor (RolAutor): Rol específico del autor en el paper.
    """
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, verbose_name="Paper")
    autor = models.ForeignKey('authors.Autor', on_delete=models.CASCADE, verbose_name="Autor")
    orden_autor = models.PositiveIntegerField(default=1, verbose_name="Orden del Autor",
                                              help_text="Posición del autor en la lista (1 = primer autor)")
    rol_autor = models.ForeignKey('authors.RolAutor', on_delete=models.CASCADE, verbose_name="Rol del Autor")

    class Meta:
        managed = True
        verbose_name = "Autor del Paper"
        verbose_name_plural = "Autores del Paper"
        ordering = ['orden_autor']
        unique_together = ['paper', 'autor']

    def __str__(self):
        """Devuelve una representación legible del autor y su paper."""
        return f"{self.autor.nombre} - {self.paper.titulo}"

    def set_orden_autor(self, orden):
        """
        Asigna el orden del autor en la lista.

        Args:
            orden (int): Posición del autor (mayor que 0).

        Raises:
            ValueError: Si el orden es menor o igual a cero.
        """
        if orden > 0:
            self.orden_autor = orden
        else:
            raise ValueError("El orden del autor debe ser mayor a 0")

    def get_orden_autor(self):
        """
        Obtiene el orden actual del autor.

        Returns:
            int: Número de orden del autor.
        """
        return self.orden_autor

    @property
    def es_primer_autor(self):
        """
        Indica si el autor ocupa la primera posición.

        Returns:
            bool: True si es el primer autor.
        """
        return self.orden_autor == 1

    @property
    def es_autor_correspondiente(self):
        """
        Indica si el autor es el correspondiente (último de la lista).

        Returns:
            bool: True si ocupa la última posición.
        """
        if not hasattr(self, "_max_orden"):
            self._max_orden = (
                PaperAutor.objects.filter(paper=self.paper)
                .aggregate(models.Max('orden_autor'))['orden_autor__max']
            )
        return self.orden_autor == self._max_orden

    @property
    def posicion_texto(self):
        """
        Devuelve la posición del autor en formato textual.

        Returns:
            str: Texto descriptivo (Primer autor, Autor correspondiente, etc.).
        """
        if self.es_primer_autor:
            return "Primer autor"
        elif self.es_autor_correspondiente:
            return "Autor correspondiente"
        return f"Autor #{self.orden_autor}"
