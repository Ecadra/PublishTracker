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
    Actualiza la aplicación forzando la sincronización con la rama 'main' del repositorio remoto.
    Este método es más robusto y funciona incluso desde un estado 'detached HEAD'.
    """
    try:
        project_root = settings.BASE_DIR.parent
        git_dir = os.path.join(project_root, '.git')

        if not os.path.isdir(git_dir):
            return JsonResponse({
                'success': False,
                'message': 'Error: El directorio .git no se encontró. La actualización automática no está disponible.'
            }, status=400)

        # 1. Traer todos los cambios del repositorio remoto sin aplicarlos
        print("Ejecutando 'git fetch --all'...")
        subprocess.run(
            ['git', 'fetch', '--all'],
            capture_output=True, text=True, check=True, cwd=project_root
        )

        # 2. Asegurarse de estar en la rama principal (main o master)
        print("Cambiando a la rama 'main'...")
        subprocess.run(['git', 'checkout', 'main'], capture_output=True, text=True, cwd=project_root)

        # 3. Forzar la actualización al estado del repositorio remoto (origin/main)
        print("Forzando la actualización con 'git reset --hard origin/main'...")
        reset_result = subprocess.run(
            ['git', 'reset', '--hard', 'origin/main'],
            capture_output=True, text=True, check=True, cwd=project_root
        )
        
        output = reset_result.stdout

        return JsonResponse({
            'success': True,
            'message': '¡Actualización completada con éxito! Por favor, reinicia la aplicación.',
            'output': output
        })

    except subprocess.CalledProcessError as e:
        # Este error es común si la rama principal no es 'main', sino 'master'
        if "pathspec 'main' did not match any file(s) known to git" in e.stderr:
             try:
                print("Rama 'main' no encontrada, intentando con 'master'...")
                subprocess.run(['git', 'checkout', 'master'], check=True, capture_output=True, text=True, cwd=project_root)
                reset_result = subprocess.run(['git', 'reset', '--hard', 'origin/master'], check=True, capture_output=True, text=True, cwd=project_root)
                return JsonResponse({
                    'success': True,
                    'message': '¡Actualización completada con éxito! Por favor, reinicia la aplicación.',
                    'output': reset_result.stdout
                })
             except subprocess.CalledProcessError as master_e:
                return JsonResponse({'success': False, 'message': f"Error al intentar con 'master': {master_e.stderr}", 'output': master_e.stderr}, status=500)

        error_message = f"Error al ejecutar un comando de Git: {e.stderr}"
        return JsonResponse({
            'success': False,
            'message': error_message,
            'output': e.stderr
        }, status=500)
    except FileNotFoundError:
        return JsonResponse({
            'success': False,
            'message': 'El comando "git" no se encontró. Asegúrate de que Git esté instalado y en el PATH.'
        }, status=500)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Ocurrió un error inesperado durante la actualización: {str(e)}'
        }, status=500)