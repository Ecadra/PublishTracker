import os
import subprocess
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from config import settings
from .forms import ProgramaSecitiForm, EjeSecithiForm
from .models import ProgramaSeciti, EjeSecithi


def modal_nuevo_programa(request):
    """
    Renderiza el modal para crear un nuevo Programa SECITI.

    Crea una instancia vacía del formulario y la envía al template genérico
    para su visualización dentro de un modal.

    Args:
        request (HttpRequest): Solicitud HTTP entrante.

    Returns:
        HttpResponse: Respuesta con el modal renderizado.
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
    Renderiza el modal para crear un nuevo Eje SECITHI.

    Genera una instancia del formulario correspondiente y la muestra
    en un modal reutilizable.

    Args:
        request (HttpRequest): Solicitud HTTP entrante.

    Returns:
        HttpResponse: Respuesta con el modal renderizado.
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
    Guarda un nuevo Programa SECITI en la base de datos.

    Procesa una solicitud POST, valida el formulario y guarda
    los datos si son válidos. En caso contrario, devuelve los errores
    de validación.

    Args:
        request (HttpRequest): Solicitud HTTP con los datos del formulario.

    Returns:
        JsonResponse: Objeto JSON con el resultado de la operación.
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
    Guarda un nuevo Eje SECITHI en la base de datos.

    Procesa una solicitud POST, valida el formulario y guarda los datos
    si son válidos. Si hay errores, devuelve los detalles de validación.

    Args:
        request (HttpRequest): Solicitud HTTP con los datos del formulario.

    Returns:
        JsonResponse: Objeto JSON con el resultado de la operación.
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
    Actualiza la aplicación sincronizándola con la rama principal del repositorio remoto.

    Este método ejecuta comandos de Git directamente en el servidor,
    asegurando que el proyecto se alinee con la versión más reciente
    del repositorio remoto. Soporta entornos con 'main' o 'master'.

    Args:
        request (HttpRequest): Solicitud HTTP de tipo POST.

    Returns:
        JsonResponse: Resultado del proceso de actualización.
            - success (bool): Indica si la actualización fue exitosa.
            - message (str): Mensaje de resultado.
            - output (str): Salida del comando Git ejecutado.
    """
    try:
        project_root = settings.BASE_DIR.parent
        git_dir = os.path.join(project_root, '.git')

        # Validar existencia de repositorio Git
        if not os.path.isdir(git_dir):
            return JsonResponse({
                'success': False,
                'message': 'Error: El directorio .git no se encontró. La actualización automática no está disponible.'
            }, status=400)

        # 1. Obtener cambios del repositorio remoto
        print("Ejecutando 'git fetch --all'...")
        subprocess.run(
            ['git', 'fetch', '--all'],
            capture_output=True, text=True, check=True, cwd=project_root
        )

        # 2. Asegurarse de estar en la rama principal
        print("Cambiando a la rama 'master'...")
        subprocess.run(['git', 'checkout', 'master'], capture_output=True, text=True, cwd=project_root)

        # 3. Forzar la actualización al estado remoto
        print("Forzando actualización con 'git reset --hard origin/master'...")
        reset_result = subprocess.run(
            ['git', 'reset', '--hard', 'origin/master'],
            capture_output=True, text=True, check=True, cwd=project_root
        )

        output = reset_result.stdout
        return JsonResponse({
            'success': True,
            'message': '¡Actualización completada con éxito! Por favor, reinicia la aplicación.',
            'output': output
        })

    except subprocess.CalledProcessError as e:
        # Si la rama 'main' no existe, intentar con 'master'
        if "pathspec 'main' did not match any file(s) known to git" in e.stderr:
            try:
                print("Rama 'main' no encontrada, intentando con 'master'...")
                subprocess.run(
                    ['git', 'checkout', 'master'],
                    check=True, capture_output=True, text=True, cwd=project_root
                )
                reset_result = subprocess.run(
                    ['git', 'reset', '--hard', 'origin/master'],
                    check=True, capture_output=True, text=True, cwd=project_root
                )
                return JsonResponse({
                    'success': True,
                    'message': '¡Actualización completada con éxito! Por favor, reinicia la aplicación.',
                    'output': reset_result.stdout
                })
            except subprocess.CalledProcessError as master_e:
                return JsonResponse({
                    'success': False,
                    'message': f"Error al intentar con 'master': {master_e.stderr}",
                    'output': master_e.stderr
                }, status=500)

        # Error genérico de Git
        return JsonResponse({
            'success': False,
            'message': f"Error al ejecutar un comando de Git: {e.stderr}",
            'output': e.stderr
        }, status=500)

    except FileNotFoundError:
        # Error si Git no está instalado
        return JsonResponse({
            'success': False,
            'message': 'El comando "git" no se encontró. Asegúrate de que Git esté instalado y en el PATH.'
        }, status=500)

    except Exception as e:
        # Cualquier otro error inesperado
        return JsonResponse({
            'success': False,
            'message': f'Ocurrió un error inesperado durante la actualización: {str(e)}'
        }, status=500)
