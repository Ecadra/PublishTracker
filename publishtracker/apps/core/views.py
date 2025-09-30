

from django.shortcuts import render
from django.http import JsonResponse
from .forms import ProgramaSecitiForm, EjeSecithiForm
from .models import ProgramaSeciti, EjeSecithi # Asegúrate de importar los modelos

def modal_nuevo_programa(request):
    form = ProgramaSecitiForm()
    context = {
        'form': form,
        'titulo_modal': 'Añadir Nuevo Programa SECITI',
        'accion_guardar': 'guardarPrograma', # Nombre de la función JS para guardar
    }
    return render(request, 'modals/formulario_generico.html', context)

def modal_nuevo_eje(request):
    form = EjeSecithiForm()
    context = {
        'form': form,
        'titulo_modal': 'Añadir Nuevo Eje SECITHI',
        'accion_guardar': 'guardarEje', # Nombre de la función JS para guardar
    }
    return render(request, 'modals/formulario_generico.html', context)

def guardar_programa(request):
    if request.method == 'POST':
        form = ProgramaSecitiForm(request.POST)
        if form.is_valid():
            nuevo_programa = form.save()
            # Devuelve éxito con datos de la nueva entidad
            return JsonResponse({
                'success': True,
                'message': 'Programa SECITI guardado correctamente.',
                'objeto': {
                    'id': nuevo_programa.id,
                    'nombre': nuevo_programa.nombre,
                    # Puedes incluir más campos si es necesario para la actualización del select
                }
            })
        else:
            # Devuelve errores de validación DETALLADOS
            errors_dict = {}
            for field, error_list in form.errors.items():
                # `error_list` es una lista de mensajes de error para el campo
                # Convertimos cada error a string y lo unimos con <br> o \n si es necesario
                # Usamos str(error) para asegurar que sea un string
                errors_dict[field] = [str(error) for error in error_list]

            return JsonResponse({
                'success': False,
                'message': 'Errores de validación en uno o más campos.',
                'errors': errors_dict # Enviar el diccionario de errores
            })
    else:
        return JsonResponse({'success': False, 'message': 'Método no permitido.'})

def guardar_eje(request):
    if request.method == 'POST':
        form = EjeSecithiForm(request.POST)
        if form.is_valid():
            nuevo_eje = form.save()
            # Devuelve éxito con datos de la nueva entidad
            return JsonResponse({
                'success': True,
                'message': 'Eje SECITHI guardado correctamente.',
                'objeto': {
                    'id': nuevo_eje.id,
                    'nombre': nuevo_eje.nombre,
                    # Puedes incluir más campos si es necesario para la actualización del select
                }
            })
        else:
            # Devuelve errores de validación DETALLADOS
            errors_dict = {}
            for field, error_list in form.errors.items():
                # `error_list` es una lista de mensajes de error para el campo
                # Convertimos cada error a string y lo unimos con <br> o \n si es necesario
                # Usamos str(error) para asegurar que sea un string
                errors_dict[field] = [str(error) for error in error_list]

            return JsonResponse({
                'success': False,
                'message': 'Errores de validación en uno o más campos.',
                'errors': errors_dict # Enviar el diccionario de errores
            })
    else:
        return JsonResponse({'success': False, 'message': 'Método no permitido.'})
