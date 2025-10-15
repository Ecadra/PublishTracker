# authors/models.py
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

class Autor(models.Model):
    """
    Modelo para representar autores.
    Incluye nombre completo y ORCID con validación de formato.
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
        return self.nombre

    def set_nombre(self, nombre):
        """
        Setter para nombre: capitaliza cada palabra y elimina espacios extra.
        """
        self.nombre = ' '.join(word.capitalize() for word in nombre.strip().split())

    def get_nombre(self):
        """
        Getter para nombre.
        """
        return self.nombre

    def set_orcid(self, orcid):
        """
        Setter para ORCID: limpia, valida longitud y formatea.
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
        Getter para ORCID.
        """
        return self.orcid
    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para asegurar que la lógica de formateo
        siempre se aplique antes de guardar el objeto en la base de datos.
        """
        self.set_nombre(self.nombre)
        super().save(*args, **kwargs)
    @property
    def tiene_orcid(self):
        """
        Indica si el autor tiene un ORCID válido.
        """
        return bool(self.orcid and len(self.orcid) == 19)

    @property
    def nombre_corto(self):
        """
        Devuelve el nombre en formato: Apellido, Inicial.
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
        Devuelve la URL pública de ORCID si existe.
        """
        return f"https://orcid.org/{self.orcid}" if self.tiene_orcid else None


class Rol(models.Model):
    """
    Modelo para roles de autores (ej. 'Primer autor', 'Correspondiente', etc.).
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
        return self.nombre_rol

    def set_nombre_rol(self, nombre_rol):
        """
        Setter para nombre_rol: capitaliza y elimina espacios extra.
        """
        self.nombre_rol = nombre_rol.strip().title()

    def get_nombre_rol(self):
        """
        Getter para nombre_rol.
        """
        return self.nombre_rol

    @property
    def descripcion_corta(self):
        """
        Devuelve una versión corta de la descripción.
        """
        if self.descripcion and len(self.descripcion) > 50:
            return self.descripcion[:50] + "..."
        return self.descripcion or "Sin descripción"


class RolAutor(models.Model):
    """
    Modelo intermedio para asignar roles a autores.
    Relaciona Autor y Rol, con fecha de asignación.
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
        return f"{self.autor.nombre} - {self.rol.nombre_rol}"

    @property
    def asignacion_reciente(self):
        """
        Indica si la asignación es reciente (menos de 30 días).
        """
        from datetime import timedelta
        return timezone.now() - self.fecha_asignacion <= timedelta(days=30)


class PaperAutor(models.Model):
    """
    Modelo para relación many-to-many entre Paper y Autor, con orden y rol.
    """
    paper = models.ForeignKey(
        'publications.Paper',
        on_delete=models.CASCADE,
        verbose_name="Paper"
    )
    autor = models.ForeignKey(
        Autor,
        on_delete=models.CASCADE,
        verbose_name="Autor"
    )
    orden_autor = models.PositiveIntegerField(
        default=1,
        verbose_name="Orden del Autor",
        help_text="Posición del autor en la lista (1 = primer autor)"
    )
    rol_autor = models.ForeignKey(
        RolAutor,
        on_delete=models.CASCADE,
        verbose_name="Rol del Autor"
    )

    class Meta:
        managed = True
        verbose_name = "Autor del Paper"
        verbose_name_plural = "Autores del Paper"
        ordering = ['orden_autor']
        unique_together = ['paper', 'autor']

    def __str__(self):
        return f"{self.autor.nombre} - {self.paper.titulo}"

    def set_orden_autor(self, orden):
        """
        Setter para orden_autor: debe ser mayor a 0.
        """
        if orden > 0:
            self.orden_autor = orden
        else:
            raise ValueError("El orden del autor debe ser mayor a 0")

    def get_orden_autor(self):
        """
        Getter para orden_autor.
        """
        return self.orden_autor

    @property
    def es_primer_autor(self):
        """
        Indica si es el primer autor.
        """
        return self.orden_autor == 1

    @property
    def es_autor_correspondiente(self):
        """
        Indica si es el autor correspondiente (último en la lista).
        Optimizado para reducir consultas.
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
        Devuelve la posición del autor en texto legible.
        """
        if self.es_primer_autor:
            return "Primer autor"
        elif self.es_autor_correspondiente:
            return "Autor correspondiente"
        return f"Autor #{self.orden_autor}"
