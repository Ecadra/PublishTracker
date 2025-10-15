from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import json

from publications.models import PaperAutor
from .models import Paper, PalabraClave, PaperPalabraClave
from authors.models import Autor, Rol, RolAutor
from journals.models import Revista, Editorial, EdicionRevista, CategoriaRevista, AmbitoRevista
from core.models import Pais, EstatusPublicacion, ProgramaSeciti, EjeSecithi


class PublicationsModelTestCase(TestCase):
    """
    Pruebas unitarias para los modelos del módulo 'publications'.

    Valida la correcta creación, normalización y relaciones de los modelos
    `Paper` y `PaperAutor`.

    Métodos:
        setUp(): Crea los datos base para todas las pruebas del modelo.
        test_paper_creation_and_normalization(): Verifica que el título y DOI
            de los papers se normalicen correctamente.
        test_paper_autor_relationship(): Comprueba la relación M2M Paper-Autor.
    """

    def setUp(self):
        """
        Configura los datos iniciales para las pruebas de modelos.

        Crea los catálogos mínimos requeridos (País, Editorial, Categoría,
        Ámbito y Revista), además de los objetos Autor, Rol y RolAutor.
        """
        pais = Pais.objects.create(nombre="Testlandia", codigo_iso="TLD")
        editorial = Editorial.objects.create(nombre="Editorial Científica", pais=pais)
        categoria = CategoriaRevista.objects.create(nombre="Interdisciplinaria")
        ambito = AmbitoRevista.objects.create(nombre="Internacional")
        revista = Revista.objects.create(
            nombre="Journal of Everything",
            issn_electronico="1234-567X",
            editorial=editorial,
            pais_publicacion=pais,
            categoria=categoria,
            ambito=ambito
        )

        self.edicion = EdicionRevista.objects.create(revista=revista, anio=2024, volumen="1", numero="1")
        self.estatus = EstatusPublicacion.objects.create(estatus="Publicado")
        self.autor = Autor.objects.create(nombre="Dr. Juan Pérez")
        self.rol = Rol.objects.create(nombre_rol="Autor Principal")
        self.rol_autor = RolAutor.objects.create(rol=self.rol, autor=self.autor)

    def test_paper_creation_and_normalization(self):
        """
        Verifica la creación y normalización del modelo Paper.

        Comprueba que los campos `titulo` y `doi` se limpien correctamente
        y que la representación en cadena sea la esperada.
        """
        paper = Paper.objects.create(
            edicion=self.edicion,
            doi="  https://doi.org/10.1000/12345  ",
            titulo="   Un Título de Investigación   ",
            anio_publicacion=2024,
            estatus_publicacion=self.estatus
        )

        self.assertEqual(paper.titulo, "Un Título de Investigación")
        self.assertEqual(paper.doi, "10.1000/12345")
        self.assertEqual(paper.doi_url, "https://doi.org/10.1000/12345")
        self.assertEqual(str(paper), "Un Título de Investigación (2024)")

    def test_paper_autor_relationship(self):
        """
        Verifica la relación many-to-many entre Paper y Autor mediante PaperAutor.

        Crea un paper con un autor asignado, valida que la relación se guarde
        correctamente y que el nombre del autor asociado sea el esperado.
        """
        paper = Paper.objects.create(
            edicion=self.edicion,
            titulo="Paper con Autores",
            anio_publicacion=2024,
            estatus_publicacion=self.estatus
        )

        PaperAutor.objects.create(
            paper=paper,
            autor=self.autor,
            orden_autor=1,
            rol_autor=self.rol_autor
        )

        self.assertEqual(paper.autores.count(), 1)
        self.assertEqual(paper.autores.first().nombre, "Dr. Juan Pérez")


class PublicationsViewsTestCase(TestCase):
    """
    Pruebas unitarias para las vistas del módulo 'publications'.

    Verifica la correcta funcionalidad de la lista de papers, filtros de
    búsqueda y creación de nuevos registros mediante POST.

    Métodos:
        setUp(): Prepara los datos base para las pruebas de vistas.
        test_paper_list_view(): Comprueba la carga de la vista de listado.
        test_paper_list_view_search_filter(): Valida el filtro de búsqueda.
        test_create_paper_success(): Prueba el flujo exitoso de creación.
        test_create_paper_validation_error(): Verifica errores de validación.
    """

    def setUp(self):
        """
        Configura los datos iniciales para las pruebas de vistas.

        Crea catálogos, revistas, autores y un paper base para la lista.
        """
        self.client = Client()

        pais = Pais.objects.create(nombre="México", codigo_iso="MEX")
        editorial = Editorial.objects.create(nombre="Editorial de Pruebas", pais=pais)
        categoria = CategoriaRevista.objects.create(nombre="Tecnología")
        ambito = AmbitoRevista.objects.create(nombre="Nacional")
        self.revista = Revista.objects.create(
            nombre="Revista de Django Testing",
            issn_electronico="1111-222X",
            editorial=editorial,
            pais_publicacion=pais,
            categoria=categoria,
            ambito=ambito
        )
        self.edicion = EdicionRevista.objects.create(revista=self.revista, anio=2023, volumen="2", numero="3")

        self.estatus_publicado = EstatusPublicacion.objects.create(estatus="Publicado")
        self.estatus_en_proceso = EstatusPublicacion.objects.create(estatus="En Proceso")
        self.programa_seciti = ProgramaSeciti.objects.create(nombre="Fondo de Innovación")
        self.eje_secithi = EjeSecithi.objects.create(nombre="Desarrollo Sostenible")

        self.autor1 = Autor.objects.create(nombre="Ana Torres", orcid="0000-0001-0002-0003")
        self.rol1 = Rol.objects.create(nombre_rol="Autor de correspondencia")
        self.rol_autor1 = RolAutor.objects.create(rol=self.rol1, autor=self.autor1)

        self.paper1 = Paper.objects.create(
            edicion=self.edicion,
            titulo="Introducción a las Pruebas en Django",
            anio_publicacion=2023,
            estatus_publicacion=self.estatus_publicado,
            doi="10.1234/django.test.1"
        )

    def test_paper_list_view(self):
        """
        Verifica la carga correcta de la vista de listado de papers.

        Comprueba que el template y el contenido mostrado sean los esperados.
        """
        response = self.client.get(reverse('publications:mis papers'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'publications/paper_list_template.html')
        self.assertContains(response, self.paper1.titulo)

    def test_paper_list_view_search_filter(self):
        """
        Verifica el filtro de búsqueda en la lista de papers.

        Comprueba que se muestren solo los resultados que coincidan con el
        término de búsqueda.
        """
        response = self.client.get(reverse('publications:mis papers'), {'search': 'Django'})
        self.assertContains(response, self.paper1.titulo)

        response_no_match = self.client.get(reverse('publications:mis papers'), {'search': 'Flask'})
        self.assertNotContains(response_no_match, self.paper1.titulo)

    def test_create_paper_success(self):
        """
        Prueba el flujo completo de creación de un paper (caso exitoso).

        Envía una solicitud POST con datos válidos, autores y palabras clave,
        y valida la creación de los objetos relacionados.
        """
        autores_data = json.dumps([
            {'autor_id': self.autor1.id, 'orden': 1, 'rol_id': self.rol1.id}
        ])
        palabras_clave_data = json.dumps([
            {'id': None, 'nombre': 'testing'},
            {'id': None, 'nombre': 'django'}
        ])
        post_data = {
            'titulo': 'Mi Nuevo Paper de Prueba',
            'anio_publicacion': 2024,
            'estatus_publicacion': self.estatus_en_proceso.id,
            'revista': self.revista.id,
            'volumen': '3',
            'numero': '1',
            'indice_revista': 'Scopus',
            'doi': '10.9999/test.paper.1',
            'url_cita': 'http://example.com/cita',
            'total_citas': 10,
            'pagina_inicio': 1,
            'pagina_fin': 15,
            'objetivo': 'Probar la creación de papers.',
            'descripcion': 'Una descripción detallada.',
            'abstract': 'Un abstract conciso.',
            'proposito': 'Generación de conocimiento',
            'recibio_apoyo_seciti': 'true',
            'programa_seciti': self.programa_seciti.id,
            'eje_secithi': self.eje_secithi.id,
            'autores': autores_data,
            'palabras_clave': palabras_clave_data,
        }

        response = self.client.post(reverse('publications:create_paper'), post_data)
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])

        new_paper = Paper.objects.get(id=response_data['paper_id'])
        self.assertEqual(new_paper.titulo, 'Mi Nuevo Paper de Prueba')
        self.assertTrue(new_paper.recibio_apoyo_seciti)
        self.assertEqual(new_paper.programa, self.programa_seciti)
        self.assertEqual(new_paper.autores.count(), 1)
        self.assertEqual(new_paper.paperpalabraclave_set.count(), 2)
        self.assertTrue(PalabraClave.objects.filter(nombre='testing').exists())

    def test_create_paper_validation_error(self):
        """
        Verifica la respuesta de error ante un intento de creación inválido.

        Envía un formulario incompleto y valida el código HTTP 400 junto con
        la estructura del mensaje de error.
        """
        post_data = {'titulo': 'Paper incompleto'}
        response = self.client.post(reverse('publications:create_paper'), post_data)

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('message', response_data)
