import os
from django.shortcuts import render
from django.http import JsonResponse

from config import settings
from .forms import ProgramaSecitiForm, EjeSecithiForm
from .models import ProgramaSeciti, EjeSecithi
import subprocess
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


def modal_nuevo_programa(request):
    """
    Renderizar el modal para crear un programa SECITI.
    Pasos:
    1. Crear instancia del formulario
    2. Preparar contexto
    3. Renderizar template
    """
    # 1. Crear instancia del formulario
    form = ProgramaSecitiForm()

    # 2. Preparar contexto
    context = {
        'form': form,
        'titulo_modal': 'Añadir Nuevo Programa SECITI',
        'accion_guardar': 'guardarPrograma',
    }

    # 3. Renderizar template
    return render(request, 'modals/formulario_generico.html', context)


def modal_nuevo_eje(request):
    """
    Renderizar el modal para crear un eje SECITHI.
    Pasos:
    1. Crear instancia del formulario
    2. Preparar contexto
    3. Renderizar template
    """
    # 1. Crear instancia del formulario
    form = EjeSecithiForm()

    # 2. Preparar contexto
    context = {
        'form': form,
        'titulo_modal': 'Añadir Nuevo Eje SECITHI',
        'accion_guardar': 'guardarEje',
    }

    # 3. Renderizar template
    return render(request, 'modals/formulario_generico.html', context)


def guardar_programa(request):
    """
    Guardar un nuevo programa SECITI.
    Pasos:
    1. Validar método HTTP
    2. Crear y validar formulario
    3. Guardar y retornar éxito
    4. Construir y retornar errores de validación
    5. Retornar error por método no permitido
    """
    # 1. Validar método HTTP
    if request.method == 'POST':
        # 2. Crear y validar formulario
        form = ProgramaSecitiForm(request.POST)

        if form.is_valid():
            # 3. Guardar y retornar éxito
            nuevo_programa = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Programa SECITI guardado correctamente.',
                'objeto': {
                    'id': nuevo_programa.id,
                    'nombre': nuevo_programa.nombre
                }
            })

        # 4. Construir y retornar errores de validación
        errors_dict = {
            field: [str(error) for error in error_list]
            for field, error_list in form.errors.items()
        }
        return JsonResponse({
            'success': False,
            'message': 'Errores de validación en uno o más campos.',
            'errors': errors_dict
        })

    # 5. Retornar error por método no permitido
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido.'
    })


def guardar_eje(request):
    """
    Guardar un nuevo eje SECITHI.
    Pasos:
    1. Validar método HTTP
    2. Crear y validar formulario
    3. Guardar y retornar éxito
    4. Construir y retornar errores de validación
    5. Retornar error por método no permitido
    """
    # 1. Validar método HTTP
    if request.method == 'POST':
        # 2. Crear y validar formulario
        form = EjeSecithiForm(request.POST)

        if form.is_valid():
            # 3. Guardar y retornar éxito
            nuevo_eje = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Eje SECITHI guardado correctamente.',
                'objeto': {
                    'id': nuevo_eje.id,
                    'nombre': nuevo_eje.nombre
                }
            })

        # 4. Construir y retornar errores de validación
        errors_dict = {
            field: [str(error) for error in error_list]
            for field, error_list in form.errors.items()
        }
        return JsonResponse({
            'success': False,
            'message': 'Errores de validación en uno o más campos.',
            'errors': errors_dict
        })

    # 5. Retornar error por método no permitido
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido.'
    })
@require_http_methods(["POST"])
def apply_update(request):
    """
    Ejecuta actualización con 'git pull' y responde el resultado.
    Pasos:
    1. Validar que el proyecto sea un repositorio Git
    2. Ejecutar 'git pull' en la raíz del proyecto
    3. Retornar respuesta exitosa con la salida
    4. Manejar errores de ejecución de git
    5. Manejar ausencia del binario git
    6. Manejar errores inesperados
    """
    try:
        # 1. Validar repositorio Git
        project_root = settings.BASE_DIR.parent
        git_dir = os.path.join(project_root, '.git')

        if not os.path.isdir(git_dir):
            return JsonResponse({
                'success': False,
                'message': 'Error: El directorio .git no se encontró. Asegúrate de que el proyecto es un repositorio de Git.'
            }, status=400)

        # 2. Ejecutar 'git pull'
        result = subprocess.run(
            ['git', 'pull'],
            capture_output=True,
            text=True,
            check=True,
            cwd=project_root
        )

        # 3. Retornar éxito
        return JsonResponse({
            'success': True,
            'message': '¡Actualización completada! Por favor, reinicia la aplicación para ver los cambios.',
            'output': result.stdout
        })

    except subprocess.CalledProcessError as e:
        # 4. Manejar errores de git
        return JsonResponse({
            'success': False,
            'message': 'Error al ejecutar git pull. Revisa si hay conflictos sin resolver.',
            'output': e.stderr
        }, status=500)

    except FileNotFoundError:
        # 5. Manejar ausencia de git
        return JsonResponse({
            'success': False,
            'message': 'El comando "git" no se encontró. Asegúrate de que Git esté instalado y en el PATH del sistema.'
        }, status=500)

    except Exception as e:
        # 6. Manejar error inesperado
        return JsonResponse({
            'success': False,
            'message': f'Ocurrió un error inesperado: {str(e)}'
        }, status=500)