# publishtracker/apps/authors/tests.py
import json
from django.test import TestCase, Client
from django.urls import reverse
from .models import Autor, Rol
from .forms import AutorForm

class AuthorModelTest(TestCase):
    """
    Pruebas para el modelo Autor.
    Aquí nos aseguramos de que la lógica dentro del modelo, como la validación
    y el formateo de datos (nombre y ORCID), funcione correctamente.
    """

    def test_creacion_autor_simple(self):
        """Prueba la creación de un autor solo con el nombre."""
        autor = Autor.objects.create(nombre=" edwin campos dragusin ")
        # Verificamos que el setter `set_nombre` implícito en el guardado
        # capitalice y limpie los espacios del nombre.
        self.assertEqual(autor.nombre, "Edwin Campos Dragusin")
        self.assertIsNone(autor.orcid)

    def test_creacion_autor_con_orcid(self):
        """Prueba la creación de un autor con un ORCID y verifica su formato."""
        autor = Autor.objects.create(
            nombre="Jane Doe",
            orcid="0000-0002-1825-0097"
        )
        self.assertEqual(autor.nombre, "Jane Doe")
        self.assertEqual(autor.orcid, "0000-0002-1825-0097")
        self.assertTrue(autor.tiene_orcid)
        self.assertEqual(autor.orcid_url, "https://orcid.org/0000-0002-1825-0097")

    def test_nombre_corto_property(self):
        """Prueba la propiedad `nombre_corto` que formatea el nombre."""
        autor = Autor(nombre="John Ronald Reuel Tolkien")
        self.assertEqual(autor.nombre_corto, "Ronald Reuel Tolkien, J.")

    def test_setters_directos(self):
        """Prueba los setters del modelo de forma explícita."""
        autor = Autor()
        autor.set_nombre("  alan turing  ")
        autor.set_orcid("0000000123456789")
        autor.save()
        
        autor_db = Autor.objects.get(id=autor.id)
        self.assertEqual(autor_db.nombre, "Alan Turing")
        self.assertEqual(autor_db.get_orcid(), "0000-0001-2345-6789")

    def test_orcid_invalido(self):
        """Prueba que un ORCID con formato incorrecto lance un error de validación."""
        autor = Autor()
        # Usamos `assertRaises` para confirmar que se produce un error esperado.
        with self.assertRaises(ValueError):
            autor.set_orcid("esto-no-es-un-orcid")


class AuthorFormTest(TestCase):
    """
    Pruebas para el formulario AutorForm.
    Validamos que el formulario limpie y valide los datos
    ingresados por el usuario como se espera.
    """

    def test_form_valido(self):
        """Prueba que el formulario sea válido con datos correctos."""
        form_data = {'nombre': 'Ada Lovelace', 'orcid': '0000-0002-1825-0098'}
        form = AutorForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_sin_orcid(self):
        """Prueba que el formulario sea válido sin un ORCID (es opcional)."""
        form_data = {'nombre': 'Charles Babbage'}
        form = AutorForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_orcid_invalido(self):
        """Prueba que el formulario no sea válido si el ORCID tiene mal formato."""
        form_data = {'nombre': 'Test Name', 'orcid': 'orcid-invalido'}
        form = AutorForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('orcid', form.errors)

    def test_form_clean_nombre(self):
        """Verifica que el método clean_nombre formatee el nombre correctamente."""
        form_data = {'nombre': '  grace hopper '}
        form = AutorForm(data=form_data)
        self.assertTrue(form.is_valid())
        # `cleaned_data` contiene los datos después de pasar por los métodos de limpieza.
        self.assertEqual(form.cleaned_data['nombre'], 'Grace Hopper')


class AuthorViewsTest(TestCase):
    """
    Pruebas para las vistas de la aplicación de autores.
    Utilizamos el cliente de pruebas de Django para simular peticiones HTTP
    y verificar las respuestas de nuestras vistas.
    """

    def setUp(self):
        """
        El método `setUp` se ejecuta antes de cada prueba. Es ideal para crear
        los objetos que usaremos en múltiples pruebas, como el cliente y datos iniciales.
        """
        self.client = Client()
        self.autor1 = Autor.objects.create(nombre="Marie Curie", orcid="0000-0001-2345-6789")
        self.autor2 = Autor.objects.create(nombre="Albert Einstein")
        self.rol_principal = Rol.objects.create(nombre_rol="Autor (a) principal")

    def test_modal_nuevo_autor_view(self):
        """Prueba que la vista que renderiza el modal de nuevo autor funcione."""
        url = reverse('modal_nuevo_autor') # Usamos `reverse` para no hardcodear la URL.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'modals/formulario_generico.html')

    def test_guardar_autor_view_valido(self):
        """Prueba el guardado de un autor a través de la vista con datos válidos."""
        url = reverse('guardar_autor')
        data = {'nombre': 'Isaac Newton', 'orcid': '0000-0003-1234-5678'}
        
        # Simulamos una petición POST con AJAX.
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['objeto']['nombre'], 'Isaac Newton')
        
        # Verificamos que el autor se haya creado en la base de datos.
        self.assertTrue(Autor.objects.filter(nombre="Isaac Newton").exists())

    def test_guardar_autor_view_invalido(self):
        """Prueba el guardado de un autor con datos inválidos (nombre vacío)."""
        url = reverse('guardar_autor')
        data = {'nombre': ''}
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('errors', response_data)
        self.assertIn('nombre', response_data['errors'])

    def test_get_roles_api_view(self):
        """Prueba la API que devuelve la lista de roles."""
        url = reverse('get_roles')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(len(response_data['roles']), 1)
        self.assertEqual(response_data['roles'][0]['nombre_rol'], 'Autor (a) principal')

    def test_search_authors_api_view(self):
        """Prueba la API de búsqueda de autores."""
        url = reverse('search_authors') + '?q=Curie'
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]['nombre'], 'Marie Curie')
