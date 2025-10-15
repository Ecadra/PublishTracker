from django.shortcuts import render
from django.http import JsonResponse
from .forms import ProgramaSecitiForm, EjeSecithiForm
from .models import ProgramaSeciti, EjeSecithi


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
