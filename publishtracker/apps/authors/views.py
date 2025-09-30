from django.shortcuts import render

# Create your views here.
# authors/views/api_views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from django.db import models
from .forms import AutorForm
from .models import Autor, Rol

@require_http_methods(["GET"])
@csrf_exempt
def search_authors(request):
    q = request.GET.get('q', '')
    if not q:
        return JsonResponse({'error': 'Parámetro q requerido'}, status=400)

    autores = Autor.objects.filter(
        models.Q(nombre__icontains=q) | models.Q(orcid__icontains=q)
    )[:10]  # Limitar a 10 resultados

    data = [
        {
            'id': autor.id,
            'nombre': autor.nombre,
            'orcid': autor.orcid
        }
        for autor in autores
    ]

    return JsonResponse(data, safe=False)

@require_http_methods(["GET"])
def get_roles(request):
    """API para obtener todos los roles disponibles"""
    try:
        roles = Rol.objects.all().values('id', 'nombre_rol', 'descripcion')
        roles_list = list(roles)
        print("Roles obtenidos:", roles_list)  # Depuración
        return JsonResponse({'success': True, 'roles': roles_list})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
def modal_nuevo_autor(request):
    form = AutorForm()
    context = {
        'form': form,
        'titulo_modal': 'Añadir Nuevo Autor',
        'accion_guardar': 'guardarAutorDesdeModal', # Nombre de la función JS para guardar
    }
    return render(request, 'modals/formulario_generico.html', context)

def guardar_autor(request):
    if request.method == 'POST':
        form = AutorForm(request.POST)
        if form.is_valid():
            nuevo_autor = form.save() # El clean ya formateó los datos
            return JsonResponse({
                'success': True,
                'message': 'Autor guardado correctamente.',
                'objeto': {
                    'id': nuevo_autor.id,
                    'nombre': nuevo_autor.nombre,
                    'orcid': nuevo_autor.orcid or '', # Enviar vacío si no tiene ORCID
                    'tiene_orcid': nuevo_autor.tiene_orcid,
                    'orcid_url': nuevo_autor.orcid_url or '', # Opcional: URL para el enlace
                }
            })
        else:
            errors_dict = {}
            for field, error_list in form.errors.items():
                errors_dict[field] = [str(error) for error in error_list]
            return JsonResponse({
                'success': False,
                'message': 'Errores de validación en uno o más campos.',
                'errors': errors_dict
            })
    else:
        return JsonResponse({'success': False, 'message': 'Método no permitido.'})