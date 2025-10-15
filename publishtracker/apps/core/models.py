from django.db import models


class Pais(models.Model):
    """
    Representa un país dentro del sistema.

    Contiene el nombre y el código ISO de tres letras, utilizados
    para identificar de manera única cada país.

    Attributes:
        nombre (str): Nombre completo del país.
        codigo_iso (str): Código ISO de tres letras (único).
    """

    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    codigo_iso = models.CharField(max_length=3, unique=True, verbose_name="Código ISO")

    class Meta:
        managed = True
        verbose_name = "País"
        verbose_name_plural = "Países"
        ordering = ["nombre"]

    def __str__(self):
        """Devuelve el nombre del país."""
        return self.nombre

    @property
    def nombre_completo(self):
        """
        Devuelve una representación completa del país.

        Returns:
            str: Nombre junto con el código ISO, por ejemplo "México (MEX)".
        """
        return f"{self.nombre} ({self.codigo_iso})"

    def clean(self):
        """
        Normaliza los valores antes de guardar.

        Ajusta la capitalización del nombre y convierte el código ISO a mayúsculas.
        """
        if self.nombre:
            self.nombre = self.nombre.strip().title()
        if self.codigo_iso:
            self.codigo_iso = self.codigo_iso.strip().upper()


class EstatusPublicacion(models.Model):
    """
    Define los posibles estatus de una publicación académica.

    Se utiliza para categorizar los estados del proceso editorial
    (por ejemplo: "En revisión", "Aceptada", "Publicada").

    Attributes:
        estatus (str): Nombre único del estatus.
        descripcion (str): Texto descriptivo opcional.
    """

    estatus = models.CharField(max_length=50, unique=True, verbose_name="Estatus")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        managed = True
        verbose_name = "Estatus de Publicación"
        verbose_name_plural = "Estatus de Publicaciones"
        ordering = ["estatus"]

    def __str__(self):
        """Devuelve el nombre del estatus."""
        return self.estatus

    def clean(self):
        """
        Normaliza el valor del estatus antes de guardar.

        Convierte el texto a mayúsculas y elimina espacios innecesarios.
        """
        if self.estatus:
            self.estatus = self.estatus.strip().upper()

    @property
    def tiene_descripcion(self):
        """
        Indica si el estatus posee una descripción válida.

        Returns:
            bool: True si hay una descripción no vacía, False en caso contrario.
        """
        return bool(self.descripcion and self.descripcion.strip())


class ProgramaSeciti(models.Model):
    """
    Representa un programa institucional de la SECITI.

    Contiene información general del programa, incluyendo su
    nombre único y una descripción opcional.

    Attributes:
        nombre (str): Nombre del programa.
        descripcion (str): Texto explicativo opcional.
    """

    nombre = models.CharField(max_length=200, unique=True, verbose_name="Nombre del Programa")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        managed = True
        verbose_name = "Programa SECITI"
        verbose_name_plural = "Programas SECITI"
        ordering = ["nombre"]

    def __str__(self):
        """Devuelve el nombre del programa."""
        return self.nombre

    def clean(self):
        """
        Normaliza el nombre antes de guardar.

        Convierte el texto a formato título y elimina espacios redundantes.
        """
        if self.nombre:
            self.nombre = self.nombre.strip().title()

    @property
    def descripcion_corta(self):
        """
        Devuelve una versión abreviada de la descripción.

        Returns:
            str: Primeros 100 caracteres seguidos de "..." si es más larga,
            o "Sin descripción" si está vacía.
        """
        if self.descripcion:
            return self.descripcion[:100] + "..." if len(self.descripcion) > 100 else self.descripcion
        return "Sin descripción"


class EjeSecithi(models.Model):
    """
    Representa un eje estratégico dentro del marco SECITHI.

    Cada eje describe un campo temático o de acción prioritaria
    dentro de los programas institucionales.

    Attributes:
        nombre (str): Nombre único del eje.
        descripcion (str): Descripción opcional del eje.
    """

    nombre = models.CharField(max_length=200, unique=True, verbose_name="Nombre del Eje")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        managed = True
        verbose_name = "Eje SECITHI"
        verbose_name_plural = "Ejes SECITHI"
        ordering = ["nombre"]

    def __str__(self):
        """Devuelve el nombre del eje."""
        return self.nombre

    def clean(self):
        """
        Normaliza el nombre antes de guardar.

        Ajusta la capitalización y elimina espacios sobrantes.
        """
        if self.nombre:
            self.nombre = self.nombre.strip().title()

    @property
    def descripcion_corta(self):
        """
        Devuelve una versión abreviada de la descripción.

        Returns:
            str: Texto recortado a 100 caracteres o "Sin descripción".
        """
        if self.descripcion:
            return self.descripcion[:100] + "..." if len(self.descripcion) > 100 else self.descripcion
        return "Sin descripción"
