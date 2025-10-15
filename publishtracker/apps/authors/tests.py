# publishtracker/apps/authors/tests.py

import json
from django.test import TestCase, Client
from django.urls import reverse
from .models import Autor, Rol
from .forms import AutorForm


class AuthorModelTest(TestCase):
    """
    Conjunto de pruebas unitarias para el modelo `Autor`.

    Verifica que las funcionalidades principales del modelo —incluyendo
    validaciones, formateo de nombres, generación de ORCID y propiedades
    derivadas— funcionen según lo esperado.
    """

    def test_creacion_autor_simple(self):
        """
        Verifica la creación de un autor solo con nombre.

        Comprueba que el setter de `nombre` normalice y capitalice el texto
        automáticamente al guardar.
        """
        autor = Autor.objects.create(nombre=" edwin campos dragusin ")
        # Verificamos que el setter `set_nombre` capitalice y limpie los espacios.
        self.assertEqual(autor.nombre, "Edwin Campos Dragusin")
        self.assertIsNone(autor.orcid)

    def test_creacion_autor_con_orcid(self):
        """
        Verifica la creación de un autor con ORCID válido.

        Asegura que se formatee correctamente y que las propiedades
        `tiene_orcid` y `orcid_url` sean coherentes.
        """
        autor = Autor.objects.create(
            nombre="Jane Doe",
            orcid="0000-0002-1825-0097"
        )
        self.assertEqual(autor.nombre, "Jane Doe")
        self.assertEqual(autor.orcid, "0000-0002-1825-0097")
        self.assertTrue(autor.tiene_orcid)
        self.assertEqual(autor.orcid_url, "https://orcid.org/0000-0002-1825-0097")

    def test_nombre_corto_property(self):
        """
        Prueba la propiedad `nombre_corto`.

        Comprueba que la propiedad derive correctamente un nombre abreviado
        a partir del nombre completo.
        """
        autor = Autor(nombre="John Ronald Reuel Tolkien")
        self.assertEqual(autor.nombre_corto, "Ronald Reuel Tolkien, J.")

    def test_setters_directos(self):
        """
        Valida el comportamiento de los setters del modelo.

        Asegura que `set_nombre` y `set_orcid` formateen correctamente los
        valores antes de almacenarlos.
        """
        autor = Autor()
        autor.set_nombre("  alan turing  ")
        autor.set_orcid("0000000123456789")
        autor.save()

        autor_db = Autor.objects.get(id=autor.id)
        self.assertEqual(autor_db.nombre, "Alan Turing")
        self.assertEqual(autor_db.get_orcid(), "0000-0001-2345-6789")

    def test_orcid_invalido(self):
        """
        Verifica que ORCID inválido genere una excepción.

        Raises:
            ValueError: Si el formato del ORCID no cumple con el estándar.
        """
        autor = Autor()
        with self.assertRaises(ValueError):
            autor.set_orcid("esto-no-es-un-orcid")


class AuthorFormTest(TestCase):
    """
    Pruebas unitarias para el formulario `AutorForm`.

    Valida que los métodos de limpieza (`clean_...`) apliquen las reglas
    del modelo y que las validaciones de ORCID y nombre funcionen.
    """

    def test_form_valido(self):
        """
        Verifica que el formulario sea válido con datos correctos.
        """
        form_data = {'nombre': 'Ada Lovelace', 'orcid': '0000-0002-1825-0098'}
        form = AutorForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_sin_orcid(self):
        """
        Verifica que el formulario acepte omitir el ORCID.

        Comprueba que el campo ORCID sea opcional.
        """
        form_data = {'nombre': 'Charles Babbage'}
        form = AutorForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_orcid_invalido(self):
        """
        Verifica que un ORCID con formato incorrecto sea inválido.
        """
        form_data = {'nombre': 'Test Name', 'orcid': 'orcid-invalido'}
        form = AutorForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('orcid', form.errors)

    def test_form_clean_nombre(self):
        """
        Valida la limpieza del nombre.

        Asegura que `clean_nombre` formatee el texto aplicando las reglas
        del modelo `Autor`.
        """
        form_data = {'nombre': '  grace hopper '}
        form = AutorForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['nombre'], 'Grace Hopper')


class AuthorViewsTest(TestCase):
    """
    Pruebas de integración para las vistas del módulo `authors`.

    Emplea el cliente de pruebas de Django para simular solicitudes HTTP
    y verificar la respuesta de las vistas asociadas.
    """

    def setUp(self):
        """
        Inicializa datos comunes para todas las pruebas.

        Crea un cliente de pruebas y algunos registros base
        para autores y roles.
        """
        self.client = Client()
        self.autor1 = Autor.objects.create(nombre="Marie Curie", orcid="0000-0001-2345-6789")
        self.autor2 = Autor.objects.create(nombre="Albert Einstein")
        self.rol_principal = Rol.objects.create(nombre_rol="Autor (a) principal")

    def test_modal_nuevo_autor_view(self):
        """
        Verifica la vista que renderiza el modal de creación de autor.

        Asegura que la plantilla correcta sea utilizada.
        """
        url = reverse('modal_nuevo_autor')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'modals/formulario_generico.html')

    def test_guardar_autor_view_valido(self):
        """
        Prueba la vista de guardado de autor con datos válidos.

        Simula una solicitud AJAX POST válida y verifica la respuesta.
        """
        url = reverse('guardar_autor')
        data = {'nombre': 'Isaac Newton', 'orcid': '0000-0003-1234-5678'}
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['objeto']['nombre'], 'Isaac Newton')
        self.assertTrue(Autor.objects.filter(nombre="Isaac Newton").exists())

    def test_guardar_autor_view_invalido(self):
        """
        Prueba la vista de guardado con datos inválidos.

        Envía un formulario con `nombre` vacío y verifica los errores devueltos.
        """
        url = reverse('guardar_autor')
        data = {'nombre': ''}
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('errors', response_data)
        self.assertIn('nombre', response_data['errors'])

    def test_get_roles_api_view(self):
        """
        Prueba la API que devuelve los roles de autores.

        Verifica que el formato de la respuesta sea correcto.
        """
        url = reverse('get_roles')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(len(response_data['roles']), 1)
        self.assertEqual(response_data['roles'][0]['nombre_rol'], 'Autor (a) principal')

    def test_search_authors_api_view(self):
        """
        Prueba la API de búsqueda de autores.

        Verifica que se devuelva la lista correcta filtrada por nombre.
        """
        url = reverse('search_authors') + '?q=Curie'
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]['nombre'], 'Marie Curie')
