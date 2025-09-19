# core/models.py
from django.db import models


class Pais(models.Model):
    """Modelo para representar países"""
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    codigo_iso = models.CharField(max_length=3, unique=True, verbose_name="Código ISO")

    class Meta:
        managed=True
        verbose_name = "País"
        verbose_name_plural = "Países"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    @property
    def nombre_completo(self):
        """Devuelve el nombre junto con el código ISO"""
        return f"{self.nombre} ({self.codigo_iso})"

    def clean(self):
        """Normaliza el nombre antes de guardar"""
        if self.nombre:
            self.nombre = self.nombre.strip().title()
        if self.codigo_iso:
            self.codigo_iso = self.codigo_iso.strip().upper()


class EstatusPublicacion(models.Model):
    """Modelo para representar el estatus de publicaciones"""
    estatus = models.CharField(max_length=50, unique=True, verbose_name="Estatus")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        managed=True
        verbose_name = "Estatus de Publicación"
        verbose_name_plural = "Estatus de Publicaciones"
        ordering = ["estatus"]

    def __str__(self):
        return self.estatus

    def clean(self):
        """Normaliza el estatus antes de guardar"""
        if self.estatus:
            self.estatus = self.estatus.strip().upper()

    @property
    def tiene_descripcion(self):
        """Verifica si hay descripción válida"""
        return bool(self.descripcion and self.descripcion.strip())


class ProgramaSeciti(models.Model):
    """Modelo para representar programas SECITI"""
    nombre = models.CharField(max_length=200, unique=True, verbose_name="Nombre del Programa")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        managed=True
        verbose_name = "Programa SECITI"
        verbose_name_plural = "Programas SECITI"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def clean(self):
        """Normaliza el nombre antes de guardar"""
        if self.nombre:
            self.nombre = self.nombre.strip().title()

    @property
    def descripcion_corta(self):
        """Devuelve una versión resumida de la descripción"""
        if self.descripcion:
            return self.descripcion[:100] + "..." if len(self.descripcion) > 100 else self.descripcion
        return "Sin descripción"


class EjeSecithi(models.Model):
    """Modelo para representar ejes SECITHI"""
    nombre = models.CharField(max_length=200, unique=True, verbose_name="Nombre del Eje")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        managed=True
        verbose_name = "Eje SECITHI"
        verbose_name_plural = "Ejes SECITHI"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def clean(self):
        """Normaliza el nombre antes de guardar"""
        if self.nombre:
            self.nombre = self.nombre.strip().title()

    @property
    def descripcion_corta(self):
        """Devuelve una versión resumida de la descripción"""
        if self.descripcion:
            return self.descripcion[:100] + "..." if len(self.descripcion) > 100 else self.descripcion
        return "Sin descripción"
