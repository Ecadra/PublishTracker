# publishtracker/apps/publications/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import json

# Importaciones de modelos de todas las apps necesarias
from .models import Paper, PalabraClave, PaperPalabraClave
from authors.models import Autor, Rol, RolAutor, PaperAutor
from journals.models import Revista, Editorial, EdicionRevista, CategoriaRevista, AmbitoRevista
from core.models import Pais, EstatusPublicacion, ProgramaSeciti, EjeSecithi


class PublicationsModelTestCase(TestCase):
    """
    Probar modelos de 'publications'.
    Pasos:
    1. Preparar datos base en setUp
    2. Validar normalización y representación de Paper
    3. Validar relación M2M con autores vía PaperAutor
    """

    def setUp(self):
        """
        Configurar datos base para pruebas de modelos.
        Pasos:
        1. Crear catálogos mínimos (País, Editorial, Categoría, Ámbito, Revista)
        2. Crear edición, estatus, autor y rol
        3. Preparar relación rol-autor
        """
        # 1. Crear catálogos mínimos
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

        # 2. Crear edición, estatus, autor y rol
        self.edicion = EdicionRevista.objects.create(revista=revista, anio=2024, volumen="1", numero="1")
        self.estatus = EstatusPublicacion.objects.create(estatus="Publicado")
        self.autor = Autor.objects.create(nombre="Dr. Juan Pérez")
        self.rol = Rol.objects.create(nombre_rol="Autor Principal")

        # 3. Preparar relación rol-autor
        self.rol_autor = RolAutor.objects.create(rol=self.rol, autor=self.autor)

    def test_paper_creation_and_normalization(self):
        """
        Verificar creación y normalización de Paper.
        Pasos:
        1. Crear Paper con DOI y título con espacios
        2. Validar normalización de título
        3. Validar normalización de DOI y URL derivada
        4. Validar representación __str__
        """
        # 1. Crear Paper con DOI y título con espacios
        paper = Paper.objects.create(
            edicion=self.edicion,
            doi="  https://doi.org/10.1000/12345  ",
            titulo="   Un Título de Investigación   ",
            anio_publicacion=2024,
            estatus_publicacion=self.estatus
        )

        # 2. Validar normalización de título
        self.assertEqual(paper.titulo, "Un Título de Investigación")

        # 3. Validar normalización de DOI y URL derivada
        self.assertEqual(paper.doi, "10.1000/12345")
        self.assertEqual(paper.doi_url, "https://doi.org/10.1000/12345")

        # 4. Validar representación __str__
        self.assertEqual(str(paper), "Un Título de Investigación (2024)")

    def test_paper_autor_relationship(self):
        """
        Verificar relación M2M Paper-Autor vía PaperAutor.
        Pasos:
        1. Crear Paper base
        2. Asociar autor con orden y rol
        3. Validar conteo de autores asociados
        4. Validar nombre del primer autor
        """
        # 1. Crear Paper base
        paper = Paper.objects.create(
            edicion=self.edicion,
            titulo="Paper con Autores",
            anio_publicacion=2024,
            estatus_publicacion=self.estatus
        )

        # 2. Asociar autor con orden y rol
        PaperAutor.objects.create(
            paper=paper,
            autor=self.autor,
            orden_autor=1,
            rol_autor=self.rol_autor
        )

        # 3. Validar conteo de autores asociados
        self.assertEqual(paper.autores.count(), 1)

        # 4. Validar nombre del primer autor
        self.assertEqual(paper.autores.first().nombre, "Dr. Juan Pérez")


class PublicationsViewsTestCase(TestCase):
    """
    Probar vistas de 'publications'.
    Pasos:
    1. Preparar datos base en setUp
    2. Verificar lista de papers y template
    3. Verificar filtro de búsqueda
    4. Verificar creación exitosa de Paper (happy path)
    5. Verificar errores de validación en creación
    """

    def setUp(self):
        """
        Configurar datos base para pruebas de vistas.
        Pasos:
        1. Instanciar cliente de pruebas
        2. Crear catálogos y revista con edición
        3. Crear estatus, programa y eje
        4. Crear autor, rol y relación rol-autor
        5. Crear Paper inicial para lista
        """
        # 1. Instanciar cliente de pruebas
        self.client = Client()

        # 2. Crear catálogos y revista con edición
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

        # 3. Crear estatus, programa y eje
        self.estatus_publicado = EstatusPublicacion.objects.create(estatus="Publicado")
        self.estatus_en_proceso = EstatusPublicacion.objects.create(estatus="En Proceso")
        self.programa_seciti = ProgramaSeciti.objects.create(nombre="Fondo de Innovación")
        self.eje_secithi = EjeSecithi.objects.create(nombre="Desarrollo Sostenible")

        # 4. Crear autor, rol y relación rol-autor
        self.autor1 = Autor.objects.create(nombre="Ana Torres", orcid="0000-0001-0002-0003")
        self.rol1 = Rol.objects.create(nombre_rol="Autor de correspondencia")
        self.rol_autor1 = RolAutor.objects.create(rol=self.rol1, autor=self.autor1)

        # 5. Crear Paper inicial para lista
        self.paper1 = Paper.objects.create(
            edicion=self.edicion,
            titulo="Introducción a las Pruebas en Django",
            anio_publicacion=2023,
            estatus_publicacion=self.estatus_publicado,
            doi="10.1234/django.test.1"
        )

    def test_paper_list_view(self):
        """
        Verificar vista de lista de papers.
        Pasos:
        1. Solicitar ruta de lista
        2. Validar código de estado 200
        3. Validar template utilizado
        4. Validar presencia del título del paper
        """
        # 1. Solicitar ruta de lista
        response = self.client.get(reverse('publications:mis papers'))

        # 2. Validar código de estado 200
        self.assertEqual(response.status_code, 200)

        # 3. Validar template utilizado
        self.assertTemplateUsed(response, 'publications/paper_list_template.html')

        # 4. Validar presencia del título del paper
        self.assertContains(response, self.paper1.titulo)

    def test_paper_list_view_search_filter(self):
        """
        Verificar filtro de búsqueda en lista.
        Pasos:
        1. Consultar con término coincidente
        2. Validar inclusión del paper esperado
        3. Consultar con término no coincidente
        4. Validar exclusión del paper esperado
        """
        # 1. Consultar con término coincidente
        response = self.client.get(reverse('publications:mis papers'), {'search': 'Django'})

        # 2. Validar inclusión del paper esperado
        self.assertContains(response, self.paper1.titulo)

        # 3. Consultar con término no coincidente
        response_no_match = self.client.get(reverse('publications:mis papers'), {'search': 'Flask'})

        # 4. Validar exclusión del paper esperado
        self.assertNotContains(response_no_match, self.paper1.titulo)

    def test_create_paper_success(self):
        """
        Verificar creación exitosa de paper (happy path).
        Pasos:
        1. Construir payload con autores y palabras clave
        2. Enviar POST a la vista de creación
        3. Validar respuesta exitosa y extraer ID
        4. Verificar persistencia de Paper y relaciones
        """
        # 1. Construir payload con autores y palabras clave
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

        # 2. Enviar POST a la vista de creación
        response = self.client.post(reverse('publications:create_paper'), post_data)

        # 3. Validar respuesta exitosa y extraer ID
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])

        # 4. Verificar persistencia de Paper y relaciones
        new_paper = Paper.objects.get(id=response_data['paper_id'])
        self.assertEqual(new_paper.titulo, 'Mi Nuevo Paper de Prueba')
        self.assertTrue(new_paper.recibio_apoyo_seciti)
        self.assertEqual(new_paper.programa, self.programa_seciti)
        self.assertEqual(new_paper.autores.count(), 1)
        self.assertEqual(new_paper.paperpalabraclave_set.count(), 2)
        self.assertTrue(PalabraClave.objects.filter(nombre='testing').exists())

    def test_create_paper_validation_error(self):
        """
        Verificar error de validación al crear paper.
        Pasos:
        1. Construir payload incompleto
        2. Enviar POST a la vista de creación
        3. Validar código de estado 400
        4. Validar estructura de respuesta de error
        """
        # 1. Construir payload incompleto
        post_data = {'titulo': 'Paper incompleto'}

        # 2. Enviar POST a la vista de creación
        response = self.client.post(reverse('publications:create_paper'), post_data)

        # 3. Validar código de estado 400
        self.assertEqual(response.status_code, 400)

        # 4. Validar estructura de respuesta de error
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('message', response_data)
