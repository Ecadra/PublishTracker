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

    Esta vista recibe un parámetro `q` mediante una solicitud GET
    y devuelve una lista de autores que coincidan parcial o totalmente
    con el nombre u ORCID proporcionado.

    Args:
        request (HttpRequest): Objeto de solicitud HTTP que contiene
            el parámetro de búsqueda `q`.

    Returns:
        JsonResponse: Lista de autores encontrados (máx. 10) con
            sus campos `id`, `nombre` y `orcid`. Si falta el parámetro `q`,
            devuelve un error 400.
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
    Obtiene la lista completa de roles de autores disponibles.

    Realiza una consulta a la base de datos sobre el modelo `Rol`
    y devuelve su información en formato JSON.

    Args:
        request (HttpRequest): Solicitud HTTP entrante.

    Returns:
        JsonResponse: Objeto con una lista de roles, cada uno con
        `id`, `nombre_rol` y `descripcion`. En caso de error, devuelve
        un mensaje con el detalle de la excepción y código 500.
    """
    try:
        # 1 y 2. Consultar roles y convertir a lista
        roles_list = list(Rol.objects.all().values('id', 'nombre_rol', 'descripcion'))
        return JsonResponse({'success': True, 'roles': roles_list})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def modal_nuevo_autor(request):
    """
    Renderiza el modal para la creación de un nuevo autor.

    Crea una instancia vacía de `AutorForm` y renderiza el
    template genérico del formulario dentro de un modal.

    Args:
        request (HttpRequest): Solicitud HTTP entrante.

    Returns:
        HttpResponse: Plantilla HTML renderizada con el contexto
        correspondiente (formulario, título, y acción).
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

    Procesa una solicitud POST con los datos del formulario `AutorForm`,
    valida los campos, guarda el autor y retorna una respuesta JSON
    indicando el resultado de la operación.

    Args:
        request (HttpRequest): Solicitud HTTP, debe ser de tipo POST
        y contener los datos del autor.

    Returns:
        JsonResponse: Si es exitoso, contiene los datos del nuevo autor.
        En caso de error, incluye los mensajes de validación.
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
