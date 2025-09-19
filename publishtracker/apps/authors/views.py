from django.shortcuts import render

# Create your views here.
# authors/views/api_views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from django.db import models
from .models import PaperAutor  # Asegúrate de tener este modelo
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
