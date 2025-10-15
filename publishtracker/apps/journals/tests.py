# publishtracker/apps/journals/tests.py
from django.test import TestCase, Client
from django.urls import reverse
import json

from .models import Editorial, CategoriaRevista, AmbitoRevista, Revista, EdicionRevista
from core.models import Pais

class JournalsModelTestCase(TestCase):
    """
    Pruebas unitarias para los modelos de la aplicación 'journals'.
    """

    def setUp(self):
        """
        Configuración de datos base para las pruebas de modelos.
        """
        self.pais = Pais.objects.create(nombre="España", codigo_iso="ESP")
        self.editorial = Editorial.objects.create(nombre="   editorial de prueba   ", pais=self.pais)
        self.categoria = CategoriaRevista.objects.create(nombre="Ciencias Sociales")
        self.ambito = AmbitoRevista.objects.create(nombre="Internacional")

    def test_editorial_creation_and_normalization(self):
        """
        Verifica que el modelo Editorial normalice el nombre a Title Case.
        """
        self.editorial.save()
        self.assertEqual(self.editorial.nombre, "Editorial De Prueba")
        self.assertEqual(str(self.editorial), "Editorial De Prueba")
        self.assertEqual(self.editorial.nombre_completo, "Editorial De Prueba - España")

    def test_revista_creation_and_properties(self):
        """
        Verifica la creación del modelo Revista y el funcionamiento de sus propiedades.
        """
        revista = Revista.objects.create(
            nombre="   revista científica de prueba   ",
            issn_electronico="1234-567X",
            editorial=self.editorial,
            pais_publicacion=self.pais,
            categoria=self.categoria,
            ambito=self.ambito
        )
        self.assertEqual(revista.nombre, "Revista Científica De Prueba")
        self.assertTrue(revista.tiene_issn)
        self.assertEqual(revista.issn_principal, "1234-567X")

    def test_edicion_revista_creation_and_uniqueness(self):
        """
        Verifica la creación de una EdicionRevista y su constraint 'unique_together'.
        """
        revista = Revista.objects.create(
            nombre="Revista de Test",
            issn_impreso="9876-5432",
            editorial=self.editorial,
            pais_publicacion=self.pais,
            categoria=self.categoria,
            ambito=self.ambito
        )
        edicion = EdicionRevista.objects.create(
            revista=revista,
            anio=2023,
            volumen="10",
            numero="2"
        )
        self.assertEqual(str(edicion), "Revista De Test - 2023 Vol.10 No.2")
        self.assertEqual(edicion.nombre_corto, "Vol.10 No.2 (2023)")

        # Prueba de unicidad: Intentar crear la misma edición debe fallar
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            EdicionRevista.objects.create(
                revista=revista,
                anio=2023,
                volumen="10",
                numero="2"
            )

class JournalsViewsTestCase(TestCase):
    """
    Pruebas de integración para las vistas de la aplicación 'journals'.
    """

    def setUp(self):
        """
        Configuración inicial para las pruebas de vistas.
        """
        self.client = Client()
        self.pais = Pais.objects.create(nombre="México", codigo_iso="MEX")
        self.editorial = Editorial.objects.create(nombre="Editorial Base", pais=self.pais)
        self.categoria = CategoriaRevista.objects.create(nombre="Categoría Base")
        self.ambito = AmbitoRevista.objects.create(nombre="Ámbito Base")

    def test_modal_nueva_revista_view(self):
        """
        Verifica que la vista del modal para una nueva revista responda correctamente.
        """
        response = self.client.get(reverse('journals:modal_nueva_revista'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'modals/nueva_revista_form.html')
        self.assertIn('form', response.context)

    def test_guardar_revista_success(self):
        """
        Prueba el guardado exitoso de una nueva Revista vía AJAX (POST).
        """
        data = {
            'nombre': 'Revista de Alta Calidad',
            'issn_electronico': '1111-2222',
            'factor_impacto': 4.5,
            'pais_publicacion': self.pais.id,
            'editorial': self.editorial.id,
            'categoria': self.categoria.id,
            'ambito': self.ambito.id,
        }
        response = self.client.post(reverse('journals:guardar_revista'), data)
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertTrue(Revista.objects.filter(nombre='Revista De Alta Calidad').exists())
        self.assertEqual(response_data['objeto']['nombre'], 'Revista De Alta Calidad')

    def test_guardar_revista_validation_error(self):
        """
        Prueba que la vista de guardado de revista falle si faltan datos requeridos.
        """
        data = {'nombre': 'Revista Incompleta'} # Faltan ISSN, editorial, etc.
        response = self.client.post(reverse('journals:guardar_revista'), data)
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('errors', response_data)
        # Verifica que al menos un campo requerido esté en los errores
        self.assertTrue('issn_impreso' in response_data['errors'] or '__all__' in response_data['errors'])

    # --- Pruebas para las vistas de creación de catálogos ---

    def test_guardar_pais_success(self):
        """
        Prueba el guardado exitoso de un nuevo País.
        """
        data = {'nombre': 'Argentina', 'codigo_iso': 'ARG'}
        response = self.client.post(reverse('journals:guardar_pais'), data)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertTrue(Pais.objects.filter(codigo_iso='ARG').exists())

    def test_guardar_categoria_success(self):
        """
        Prueba el guardado exitoso de una nueva CategoriaRevista.
        """
        data = {'nombre': 'Ingeniería'}
        response = self.client.post(reverse('journals:guardar_categoria'), data)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertTrue(CategoriaRevista.objects.filter(nombre='Ingeniería').exists())

    def test_guardar_ambito_success(self):
        """
        Prueba el guardado exitoso de un nuevo AmbitoRevista.
        """
        data = {'nombre': 'Nacional'}
        response = self.client.post(reverse('journals:guardar_ambito'), data)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertTrue(AmbitoRevista.objects.filter(nombre='Nacional').exists())

    def test_guardar_editorial_success(self):
        """
        Prueba el guardado exitoso de una nueva Editorial.
        """
        data = {'nombre': 'Nueva Editorial Académica', 'pais': self.pais.id}
        response = self.client.post(reverse('journals:guardar_editorial'), data)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertTrue(Editorial.objects.filter(nombre='Nueva Editorial Académica').exists())

