# publishtracker/apps/core/tests.py
from django.test import TestCase, Client
from django.urls import reverse
import json

from .models import Pais, EstatusPublicacion, ProgramaSeciti, EjeSecithi

class CoreModelTestCase(TestCase):
    """
    Pruebas unitarias para los modelos de la aplicación 'core'.
    Verifica la correcta creación, lógica de negocio y propiedades de los modelos.
    """

    def test_pais_creation_and_normalization(self):
        """
        Verifica que el modelo Pais se crea correctamente y que el método clean
        normaliza los datos (nombre en Title Case y código ISO en mayúsculas).
        """
        pais = Pais.objects.create(nombre="   méxico   ", codigo_iso="  mxn  ")
        pais.clean()
        pais.save()

        self.assertEqual(pais.nombre, "México")
        self.assertEqual(pais.codigo_iso, "MXN")
        self.assertEqual(str(pais), "México")
        self.assertEqual(pais.nombre_completo, "México (MXN)")

    def test_estatus_publicacion_creation_and_normalization(self):
        """
        Verifica la creación y normalización del modelo EstatusPublicacion.
        El estatus debe guardarse en mayúsculas.
        """
        estatus = EstatusPublicacion.objects.create(estatus="  publicado  ")
        estatus.clean()
        estatus.save()

        self.assertEqual(estatus.estatus, "PUBLICADO")
        self.assertEqual(str(estatus), "PUBLICADO")
        self.assertTrue(estatus.tiene_descripcion is False)

        estatus_con_desc = EstatusPublicacion.objects.create(
            estatus="en revisión",
            descripcion="El paper está siendo revisado por pares."
        )
        self.assertTrue(estatus_con_desc.tiene_descripcion)

    def test_programa_seciti_creation_and_properties(self):
        """
        Verifica la creación, normalización y propiedades del modelo ProgramaSeciti.
        """
        programa = ProgramaSeciti.objects.create(
            nombre="  programa de apoyo a la investigación   ",
            descripcion="Este es un texto de descripción largo para probar la propiedad de descripción corta." * 3
        )
        programa.clean()
        programa.save()

        self.assertEqual(programa.nombre, "Programa De Apoyo A La Investigación")
        self.assertEqual(str(programa), "Programa De Apoyo A La Investigación")
        self.assertTrue(programa.descripcion_corta.endswith("..."))
        self.assertTrue(len(programa.descripcion_corta) <= 103)

    def test_eje_secithi_creation_and_properties(self):
        """
        Verifica la creación, normalización y propiedades del modelo EjeSecithi.
        """
        eje = EjeSecithi.objects.create(
            nombre="   eje de desarrollo tecnológico   ",
            descripcion="Sin descripción"
        )
        eje.clean()
        eje.save()

        self.assertEqual(eje.nombre, "Eje De Desarrollo Tecnológico")
        self.assertEqual(str(eje), "Eje De Desarrollo Tecnológico")
        self.assertEqual(eje.descripcion_corta, "Sin descripción")


class CoreViewsTestCase(TestCase):
    """
    Pruebas de integración para las vistas de la aplicación 'core'.
    Verifica que las vistas modales y los endpoints de guardado AJAX funcionen correctamente.
    """

    def setUp(self):
        """
        Configuración inicial para las pruebas de vistas.
        Se crea un cliente de prueba.
        """
        self.client = Client()
        self.guardar_programa_url = reverse('core:guardar_programa')
        self.guardar_eje_url = reverse('core:guardar_eje')
        self.modal_programa_url = reverse('core:modal_nuevo_programa')
        self.modal_eje_url = reverse('core:modal_nuevo_eje')

    def test_modal_nuevo_programa_view(self):
        """
        Verifica que la vista que renderiza el modal para un nuevo programa
        responda con un código 200 y use la plantilla correcta.
        """
        response = self.client.get(self.modal_programa_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'modals/formulario_generico.html')
        self.assertIn('form', response.context)
        self.assertEqual(response.context['titulo_modal'], 'Añadir Nuevo Programa SECITI')

    def test_modal_nuevo_eje_view(self):
        """
        Verifica que la vista que renderiza el modal para un nuevo eje
        responda con un código 200 y use la plantilla correcta.
        """
        response = self.client.get(self.modal_eje_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'modals/formulario_generico.html')
        self.assertIn('form', response.context)
        self.assertEqual(response.context['titulo_modal'], 'Añadir Nuevo Eje SECITHI')

    def test_guardar_programa_success(self):
        """
        Prueba el guardado exitoso de un nuevo Programa SECITI vía AJAX (POST).
        Debe crear el objeto en la BD y devolver un JSON de éxito.
        """
        data = {'nombre': 'Nuevo Programa de Prueba'}
        response = self.client.post(self.guardar_programa_url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ProgramaSeciti.objects.filter(nombre='Nuevo Programa De Prueba').exists())
        
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['objeto']['nombre'], 'Nuevo Programa De Prueba')

    def test_guardar_programa_validation_error(self):
        """
        Prueba que la vista de guardado de programa maneje errores de validación.
        No debe crear el objeto y debe devolver un JSON con los errores.
        """
        data = {'nombre': ''} # Nombre vacío para forzar error
        response = self.client.post(self.guardar_programa_url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ProgramaSeciti.objects.exists())
        
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('errors', response_data)
        self.assertIn('nombre', response_data['errors'])

    def test_guardar_programa_invalid_method(self):
        """
        Prueba que la vista de guardado de programa solo acepte el método POST.
        """
        response = self.client.get(self.guardar_programa_url)
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200) # La vista maneja el error y devuelve 200
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['message'], 'Método no permitido.')

    def test_guardar_eje_success(self):
        """
        Prueba el guardado exitoso de un nuevo Eje SECITHI vía AJAX (POST).
        """
        data = {'nombre': 'Nuevo Eje de Prueba'}
        response = self.client.post(self.guardar_eje_url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(EjeSecithi.objects.filter(nombre='Nuevo Eje De Prueba').exists())
        
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['objeto']['nombre'], 'Nuevo Eje De Prueba')

    def test_guardar_eje_validation_error(self):
        """
        Prueba que la vista de guardado de eje maneje errores de validación.
        """
        data = {'nombre': ''}
        response = self.client.post(self.guardar_eje_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(EjeSecithi.objects.exists())
        
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('errors', response_data)
