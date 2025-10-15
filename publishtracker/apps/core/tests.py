# publishtracker/apps/core/tests.py
import os
import json
import subprocess
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
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
class UpdateViewsTestCase(TestCase):
    """
    Pruebas dedicadas para la funcionalidad de actualización automática vía Git.
    Estas pruebas utilizan 'mocks' para simular el comportamiento de subprocess.run
    sin ejecutar realmente comandos de Git, lo que las hace rápidas y seguras.
    """

    def setUp(self):
        """
        Configuración inicial para las pruebas de la vista de actualización.
        """
        self.client = Client()
        self.apply_update_url = reverse('core:apply_update')
        self.project_root = settings.BASE_DIR.parent
        self.git_dir = os.path.join(self.project_root, '.git')

    @patch('os.path.isdir')
    @patch('subprocess.run')
    def test_apply_update_success(self, mock_subprocess_run, mock_isdir):
        """
        CASO DE PRUEBA: Actualización exitosa.
        Verifica que la vista responde correctamente cuando 'git pull' se ejecuta sin errores.
        - Mensaje: Se simula que el directorio '.git' existe.
        - Mensaje: Se simula una ejecución exitosa de 'subprocess.run' con una salida de ejemplo.
        - Resultado esperado: La respuesta JSON debe indicar éxito y contener el mensaje de 'git pull'.
        """
        print("\n--- INICIANDO PRUEBA: test_apply_update_success ---")
        print("Mensaje: Simulando que el directorio .git existe.")
        mock_isdir.return_value = True

        # Configurar el mock para simular una salida exitosa de 'git pull'
        mock_subprocess_run.return_value = MagicMock(
            stdout="Already up to date.",
            stderr="",
            check_returncode=None  # Para que check=True no falle
        )
        print("Mensaje: Simulando una ejecución exitosa de 'git pull'.")

        # Realizar la petición POST
        response = self.client.post(self.apply_update_url)
        response_data = json.loads(response.content)

        print(f"Mensaje: Respuesta del servidor: {response_data}")

        # Verificaciones
        self.assertEqual(response.status_code, 200, "El código de estado debe ser 200 (OK).")
        self.assertTrue(response_data['success'], "La respuesta debe indicar éxito.")
        self.assertIn('¡Actualización completada!', response_data['message'], "El mensaje debe notificar la finalización.")
        self.assertEqual(response_data['output'], "Already up to date.", "La salida debe coincidir con la del comando simulado.")
        print("--- PRUEBA FINALIZADA: test_apply_update_success (Éxito) ---\n")

    @patch('os.path.isdir')
    def test_apply_update_not_a_git_repo(self, mock_isdir):
        """
        CASO DE PRUEBA: El proyecto no es un repositorio de Git.
        Verifica que la vista devuelve un error si no encuentra el directorio '.git'.
        - Mensaje: Se simula que el directorio '.git' NO existe.
        - Resultado esperado: La respuesta JSON debe ser un error 400 (Bad Request).
        """
        print("\n--- INICIANDO PRUEBA: test_apply_update_not_a_git_repo ---")
        print("Mensaje: Simulando que el directorio .git NO existe.")
        mock_isdir.return_value = False

        response = self.client.post(self.apply_update_url)
        response_data = json.loads(response.content)

        print(f"Mensaje: Respuesta del servidor: {response_data}")

        self.assertEqual(response.status_code, 400, "El código de estado debe ser 400 (Bad Request).")
        self.assertFalse(response_data['success'], "La respuesta debe indicar fallo.")
        self.assertIn('El directorio .git no se encontró', response_data['message'], "El mensaje debe advertir que no se encontró el repo Git.")
        print("--- PRUEBA FINALIZADA: test_apply_update_not_a_git_repo (Éxito) ---\n")

    @patch('os.path.isdir')
    @patch('subprocess.run')
    def test_apply_update_git_command_fails(self, mock_subprocess_run, mock_isdir):
        """
        CASO DE PRUEBA: El comando 'git pull' falla.
        Verifica el manejo de errores cuando 'git pull' produce un error (ej. por conflictos).
        - Mensaje: Se simula que '.git' existe.
        - Mensaje: Se simula un error en 'subprocess.run' levantando CalledProcessError.
        - Resultado esperado: La respuesta JSON debe ser un error 500 y contener el mensaje de error de Git.
        """
        print("\n--- INICIANDO PRUEBA: test_apply_update_git_command_fails ---")
        print("Mensaje: Simulando que el directorio .git existe.")
        mock_isdir.return_value = True

        # Simular un error de 'git pull'
        error_output = "error: Your local changes to the following files would be overwritten by merge:\n\tREADME.md"
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=['git', 'pull'],
            stderr=error_output
        )
        print("Mensaje: Simulando un fallo en la ejecución de 'git pull' por conflictos locales.")

        response = self.client.post(self.apply_update_url)
        response_data = json.loads(response.content)

        print(f"Mensaje: Respuesta del servidor: {response_data}")

        self.assertEqual(response.status_code, 500, "El código de estado debe ser 500 (Server Error).")
        self.assertFalse(response_data['success'], "La respuesta debe indicar fallo.")
        self.assertIn('Error al ejecutar git pull', response_data['message'], "El mensaje debe indicar un fallo en 'git pull'.")
        self.assertEqual(response_data['output'], error_output, "La salida debe contener el error de stderr.")
        print("--- PRUEBA FINALIZADA: test_apply_update_git_command_fails (Éxito) ---\n")

    @patch('os.path.isdir')
    @patch('subprocess.run')
    def test_apply_update_git_not_found(self, mock_subprocess_run, mock_isdir):
        """
        CASO DE PRUEBA: El comando 'git' no está instalado.
        Verifica el manejo de errores si el ejecutable de 'git' no se encuentra en el sistema.
        - Mensaje: Se simula que '.git' existe.
        - Mensaje: Se simula un FileNotFoundError, que ocurre cuando el comando no existe.
        - Resultado esperado: La respuesta JSON debe ser un error 500 con un mensaje específico.
        """
        print("\n--- INICIANDO PRUEBA: test_apply_update_git_not_found ---")
        print("Mensaje: Simulando que el directorio .git existe.")
        mock_isdir.return_value = True

        # Simular que el comando 'git' no se encuentra
        mock_subprocess_run.side_effect = FileNotFoundError(
            "No such file or directory: 'git'"
        )
        print("Mensaje: Simulando que el comando 'git' no está instalado (FileNotFoundError).")

        response = self.client.post(self.apply_update_url)
        response_data = json.loads(response.content)

        print(f"Mensaje: Respuesta del servidor: {response_data}")

        self.assertEqual(response.status_code, 500, "El código de estado debe ser 500 (Server Error).")
        self.assertFalse(response_data['success'], "La respuesta debe indicar fallo.")
        self.assertIn('El comando "git" no se encontró', response_data['message'], "El mensaje debe advertir que git no está instalado.")
        print("--- PRUEBA FINALIZADA: test_apply_update_git_not_found (Éxito) ---\n")
