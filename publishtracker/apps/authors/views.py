from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import models
from .forms import AutorForm
from .models import Autor, Rol

@require_http_methods(["GET"])
@csrf_exempt
def search_authors(request):
    """
    Busca autores por nombre u ORCID.
    Pasos:
    1. Obtiene el parámetro de búsqueda 'q'
    2. Valida que el parámetro exista
    3. Realiza la búsqueda en la base de datos
    4. Formatea y retorna los resultados
    """
    # 1. Obtener parámetro de búsqueda
    q = request.GET.get('q', '')

    # 2. Validar parámetro
    if not q:
        return JsonResponse({'error': 'Parámetro q requerido'}, status=400)

    # 3. Buscar autores que coincidan con el criterio
    autores = Autor.objects.filter(
        models.Q(nombre__icontains=q) | models.Q(orcid__icontains=q)
    )[:10]  # Limitar a 10 resultados

    # 4. Formatear y retornar resultados
    data = [
        {'id': autor.id, 'nombre': autor.nombre, 'orcid': autor.orcid}
        for autor in autores
    ]
    return JsonResponse(data, safe=False)

@require_http_methods(["GET"])
def get_roles(request):
    """
    Obtiene todos los roles disponibles.
    Pasos:
    1. Consulta todos los roles
    2. Convierte el QuerySet a lista
    3. Retorna la respuesta JSON
    """
    try:
        # 1 y 2. Consultar roles y convertir a lista
        roles_list = list(Rol.objects.all().values('id', 'nombre_rol', 'descripcion'))
        return JsonResponse({'success': True, 'roles': roles_list})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def modal_nuevo_autor(request):
    """
    Renderiza el modal para crear un nuevo autor.
    Pasos:
    1. Crear instancia del formulario
    2. Preparar contexto
    3. Renderizar template
    """
    # 1. Crear formulario
    form = AutorForm()

    # 2. Preparar contexto
    context = {
        'form': form,
        'titulo_modal': 'Añadir Nuevo Autor',
        'accion_guardar': 'guardarAutorDesdeModal',
    }

    # 3. Renderizar
    return render(request, 'modals/formulario_generico.html', context)

def guardar_autor(request):
    """
    Guarda un nuevo autor en la base de datos.
    Pasos:
    1. Validar método HTTP
    2. Procesar formulario
    3. Guardar autor si es válido
    4. Retornar respuesta con resultado
    """
    # 1. Validar método HTTP
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido.'})

    # 2. Procesar formulario
    form = AutorForm(request.POST)

    # 3. Validar y guardar
    if form.is_valid():
        nuevo_autor = form.save()
        # 4. Retornar respuesta exitosa
        return JsonResponse({
            'success': True,
            'message': 'Autor guardado correctamente.',
            'objeto': {
                'id': nuevo_autor.id,
                'nombre': nuevo_autor.nombre,
                'orcid': nuevo_autor.orcid or '',
                'tiene_orcid': nuevo_autor.tiene_orcid,
                'orcid_url': nuevo_autor.orcid_url or '',
            }
        })

    # 4. Retornar errores si no es válido
    errors_dict = {
        field: [str(error) for error in error_list] 
        for field, error_list in form.errors.items()
    }
    return JsonResponse({
        'success': False,
        'message': 'Errores de validación en uno o más campos.',
        'errors': errors_dict
    })
