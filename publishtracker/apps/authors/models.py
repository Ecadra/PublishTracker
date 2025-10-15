from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


class Autor(models.Model):
    """
    Representa un autor con su nombre completo y su identificador ORCID.

    Este modelo incluye métodos para formatear, validar y obtener
    la información del autor de forma estandarizada.

    Attributes:
        nombre (str): Nombre completo del autor.
        orcid (str): Identificador ORCID con formato validado (####-####-####-####).
    """

    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre Completo"
    )
    orcid = models.CharField(
        max_length=19,
        unique=True,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$',
                message='ORCID debe tener el formato: 0000-0000-0000-0000'
            )
        ],
        verbose_name="ORCID ID",
        help_text="Formato: 0000-0000-0000-0000"
    )

    class Meta:
        managed = True
        verbose_name = "Autor"
        verbose_name_plural = "Autores"
        ordering = ['nombre']

    def __str__(self):
        """Devuelve una representación legible del autor."""
        return self.nombre

    def set_nombre(self, nombre):
        """
        Formatea el nombre del autor antes de guardarlo.

        Capitaliza cada palabra y elimina los espacios extra.

        Args:
            nombre (str): Nombre del autor sin formatear.
        """
        self.nombre = ' '.join(word.capitalize() for word in nombre.strip().split())

    def get_nombre(self):
        """
        Devuelve el nombre del autor.

        Returns:
            str: Nombre completo del autor.
        """
        return self.nombre

    def set_orcid(self, orcid):
        """
        Valida y formatea el ORCID del autor.

        Limpia espacios y guiones, valida longitud y lo guarda
        en el formato estándar ####-####-####-####.

        Args:
            orcid (str): Identificador ORCID sin formato.

        Raises:
            ValueError: Si el ORCID no contiene exactamente 16 dígitos.
        """
        if orcid:
            clean_orcid = ''.join(orcid.split()).replace('-', '')
            if len(clean_orcid) == 16:
                formatted = f"{clean_orcid[0:4]}-{clean_orcid[4:8]}-{clean_orcid[8:12]}-{clean_orcid[12:16]}"
                self.orcid = formatted
            else:
                raise ValueError("ORCID inválido, debe contener 16 dígitos")
        else:
            self.orcid = None

    def get_orcid(self):
        """
        Devuelve el ORCID del autor.

        Returns:
            str | None: ORCID formateado o None si no existe.
        """
        return self.orcid

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para aplicar el formateo de nombre.

        Asegura que el método `set_nombre` se ejecute automáticamente
        antes de guardar el registro.
        """
        self.set_nombre(self.nombre)
        super().save(*args, **kwargs)

    @property
    def tiene_orcid(self):
        """
        Indica si el autor cuenta con un ORCID válido.

        Returns:
            bool: True si el autor tiene un ORCID con formato válido.
        """
        return bool(self.orcid and len(self.orcid) == 19)

    @property
    def nombre_corto(self):
        """
        Devuelve una versión abreviada del nombre del autor.

        Formato: “Apellidos, Inicial.”

        Returns:
            str: Nombre corto formateado o nombre completo si no es posible abreviar.
        """
        partes = self.nombre.split()
        if len(partes) >= 2:
            inicial = partes[0][0].upper() + '.'
            apellidos = ' '.join(partes[1:])
            return f"{apellidos}, {inicial}"
        return self.nombre

    @property
    def orcid_url(self):
        """
        Devuelve la URL pública del perfil ORCID del autor.

        Returns:
            str | None: URL pública si existe ORCID válido; None en caso contrario.
        """
        return f"https://orcid.org/{self.orcid}" if self.tiene_orcid else None


class Rol(models.Model):
    """
    Representa un rol asignable a un autor.

    Define la función que un autor puede desempeñar dentro de una
    publicación, como "Autor principal" o "Autor correspondiente".

    Attributes:
        nombre_rol (str): Nombre descriptivo del rol.
        descripcion (str): Explicación o detalle del rol.
    """
    nombre_rol = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre del Rol"
    )
    descripcion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Descripción"
    )

    class Meta:
        managed = True
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ['nombre_rol']

    def __str__(self):
        """Devuelve el nombre del rol."""
        return self.nombre_rol

    def set_nombre_rol(self, nombre_rol):
        """
        Formatea y normaliza el nombre del rol.

        Args:
            nombre_rol (str): Nombre del rol sin formatear.
        """
        self.nombre_rol = nombre_rol.strip().title()

    def get_nombre_rol(self):
        """
        Devuelve el nombre del rol.

        Returns:
            str: Nombre descriptivo del rol.
        """
        return self.nombre_rol

    @property
    def descripcion_corta(self):
        """
        Devuelve una versión abreviada de la descripción.

        Returns:
            str: Descripción recortada a 50 caracteres o
            "Sin descripción" si no hay texto.
        """
        if self.descripcion and len(self.descripcion) > 50:
            return self.descripcion[:50] + "..."
        return self.descripcion or "Sin descripción"


class RolAutor(models.Model):
    """
    Relación intermedia entre `Autor` y `Rol`.

    Permite asignar múltiples roles a un autor y registrar
    la fecha de dicha asignación.

    Attributes:
        rol (Rol): Rol asignado al autor.
        autor (Autor): Autor al que pertenece el rol.
        fecha_asignacion (datetime): Fecha de asignación del rol.
    """
    rol = models.ForeignKey(
        Rol,
        on_delete=models.CASCADE,
        verbose_name="Rol"
    )
    autor = models.ForeignKey(
        Autor,
        on_delete=models.CASCADE,
        verbose_name="Autor"
    )
    fecha_asignacion = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha de Asignación"
    )

    class Meta:
        managed = True
        verbose_name = "Rol de Autor"
        verbose_name_plural = "Roles de Autores"
        constraints = [
            models.UniqueConstraint(fields=['rol', 'autor'], name='unique_rol_autor')
        ]
        ordering = ['-fecha_asignacion']

    def __str__(self):
        """Devuelve una representación legible de la asignación de rol."""
        return f"{self.autor.nombre} - {self.rol.nombre_rol}"

    @property
    def asignacion_reciente(self):
        """
        Indica si la asignación del rol es reciente.

        Returns:
            bool: True si la asignación fue en los últimos 30 días.
        """
        from datetime import timedelta
        return timezone.now() - self.fecha_asignacion <= timedelta(days=30)
