import os
import json
import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.db import transaction
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator
from django.core.files.storage import default_storage
from django.views.decorators.http import require_http_methods

from publications.models import Paper, PaperAutor
from authors.models import Rol, Autor, RolAutor
from publications.models import ArchivoPaper, PalabraClave, PaperPalabraClave, TipoArchivoPaper
from core.models import EstatusPublicacion, ProgramaSeciti, EjeSecithi
from journals.models import ArchivoRevista, Revista, EdicionRevista, TipoArchivoRevista


@require_http_methods(["POST"])
def create_paper(request):
    """
    Crea un nuevo Paper y todas sus relaciones asociadas de forma atómica.

    El proceso incluye:
    - Validación de revista y creación/obtención de su edición.
    - Registro y copia de archivos relacionados con la edición.
    - Creación del Paper principal con sus metadatos.
    - Asociación de autores, palabras clave y archivos específicos del Paper.

    Args:
        request (HttpRequest): Solicitud POST que contiene datos del paper, autores,
            archivos y palabras clave.

    Returns:
        JsonResponse: Respuesta JSON indicando éxito o errores de validación.
    """
    try:
        with transaction.atomic():
            revista_id = request.POST.get('revista')
            if not revista_id:
                raise ValueError("La revista es un campo requerido.")
            revista = Revista.objects.get(id=revista_id)
            anio = request.POST.get('anio_publicacion')

            edicion, _ = EdicionRevista.objects.get_or_create(
                revista=revista,
                anio=anio,
                volumen=request.POST.get('volumen'),
                numero=request.POST.get('numero'),
                defaults={'indice_revista': request.POST.get('indice_revista')}
            )

            tipos_archivo_revista_map = {
                'archivo_edicion_portada': 'Portada',
                'archivo_edicion_hoja_legal': 'Hoja Legal',
                'archivo_edicion_indice_de_paper': 'Indice de Paper',
            }
            for field_name, tipo_nombre in tipos_archivo_revista_map.items():
                if field_name in request.FILES:
                    tipo_obj = TipoArchivoRevista.objects.get(tipo=tipo_nombre)
                    ArchivoRevista.objects.update_or_create(
                        edicion=edicion,
                        tipo_archivo=tipo_obj,
                        defaults={
                            'archivo': request.FILES[field_name],
                            'nombre_archivo': request.FILES[field_name].name
                        }
                    )

            estatus_id = request.POST.get('estatus_publicacion')
            if not estatus_id:
                raise ValueError("El estatus de publicación es requerido.")
            estatus = EstatusPublicacion.objects.get(id=estatus_id)

            paper_data = {
                'titulo': request.POST.get('titulo'),
                'anio_publicacion': anio,
                'estatus_publicacion': estatus,
                'edicion': edicion,
                'doi': request.POST.get('doi'),
                'url_cita': request.POST.get('url_cita'),
                'total_citas': request.POST.get('total_citas') or 0,
                'pagina_inicio': request.POST.get('pagina_inicio'),
                'pagina_fin': request.POST.get('pagina_fin'),
                'objetivo': request.POST.get('objetivo'),
                'descripcion': request.POST.get('descripcion'),
                'abstract': request.POST.get('abstract'),
                'referencia_apa': request.POST.get('referencia_apa', ''),
                'proposito': request.POST.get('proposito'),
                'recibio_apoyo_seciti': request.POST.get('recibio_apoyo_seciti') == 'true',
            }
            if paper_data['recibio_apoyo_seciti']:
                paper_data['programa'] = ProgramaSeciti.objects.get(id=request.POST.get('programa_seciti'))
                paper_data['eje_secithi'] = EjeSecithi.objects.get(id=request.POST.get('eje_secithi'))

            paper = Paper.objects.create(**paper_data)

            clone_dir = os.path.join(str(edicion.anio), str(revista.id), str(paper.id), 'archivos_revista')
            archivos_de_la_edicion = ArchivoRevista.objects.filter(edicion=edicion)
            for archivo_revista in archivos_de_la_edicion:
                nombre_archivo_guardado = os.path.basename(archivo_revista.archivo.name)
                destination_path = os.path.join(clone_dir, nombre_archivo_guardado)
                with archivo_revista.archivo.open('rb') as original_file:
                    default_storage.save(destination_path, original_file)

            tipos_archivo_paper_map = {
                'archivo_paper': 'Paper Completo',
                'primera_pagina': 'Primera Pagina',
            }
            for field_name, tipo_nombre in tipos_archivo_paper_map.items():
                if field_name in request.FILES:
                    tipo_obj = TipoArchivoPaper.objects.get(tipo=tipo_nombre)
                    ArchivoPaper.objects.create(
                        paper=paper,
                        tipo_archivo=tipo_obj,
                        archivo=request.FILES[field_name],
                        nombre_archivo=request.FILES[field_name].name
                    )

            autores = json.loads(request.POST.get('autores', '[]'))
            if not autores:
                raise ValueError("Debe seleccionar al menos un autor.")
            for autor_data in autores:
                autor_obj = Autor.objects.get(id=autor_data['autor_id'])
                rol_obj = Rol.objects.get(id=autor_data['rol_id'])
                rol_autor, _ = RolAutor.objects.get_or_create(autor=autor_obj, rol=rol_obj)
                PaperAutor.objects.create(
                    paper=paper,
                    autor=autor_obj,
                    orden_autor=autor_data['orden'],
                    rol_autor=rol_autor
                )

            palabras_clave = json.loads(request.POST.get('palabras_clave', '[]'))
            for palabra_data in palabras_clave:
                palabra_obj, _ = PalabraClave.objects.get_or_create(
                    nombre=palabra_data['nombre'].strip().lower(),
                    defaults={'nombre': palabra_data['nombre'].strip()}
                )
                PaperPalabraClave.objects.create(paper=paper, palabra_clave=palabra_obj)

            return JsonResponse({
                'success': True,
                'message': 'Paper y todos sus archivos han sido guardados exitosamente.',
                'paper_id': paper.id
            })

    except (ValueError, KeyError, json.JSONDecodeError) as e:
        return JsonResponse({'success': False, 'message': f'Error en los datos enviados: {str(e)}'}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'message': f'Ha ocurrido un error inesperado: {str(e)}'}, status=500)


@require_http_methods(["POST"])
def create_keywords(request):
    """
    Crea una nueva palabra clave mediante JSON.

    Args:
        request (HttpRequest): Solicitud POST con JSON que contiene el campo `nombre`.

    Returns:
        JsonResponse: Objeto JSON con el resultado de la creación o error.
    """
    try:
        data = json.loads(request.body)
        nombre = data.get('nombre', '').strip().lower()
        if not nombre:
            return JsonResponse({'success': False, 'message': 'El nombre de la palabra clave es requerido'}, status=400)

        palabra_existente = PalabraClave.objects.filter(nombre__iexact=nombre).first()
        if palabra_existente:
            return JsonResponse({
                'success': True,
                'palabra_clave': {'id': palabra_existente.id, 'nombre': palabra_existente.nombre},
                'message': 'La palabra clave ya existe'
            })

        palabra_nueva = PalabraClave.objects.create(nombre=nombre)
        return JsonResponse({
            'success': True,
            'palabra_clave': {'id': palabra_nueva.id, 'nombre': palabra_nueva.nombre},
            'message': 'Palabra clave creada exitosamente'
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Error al decodificar JSON'}, status=400)
    except Exception as e:
        import traceback
        print("Error al crear palabra clave:", str(e))
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'message': f'Error al crear palabra clave: {str(e)}',
            'error_details': traceback.format_exc()
        }, status=500)


def paper_list_view(request):
    """
    Lista los papers con filtros de búsqueda, año, estatus y paginación.

    También verifica actualizaciones del repositorio en GitHub y muestra
    notificaciones si hay una nueva versión disponible.

    Args:
        request (HttpRequest): Solicitud GET con filtros opcionales `search`, `status` y `year`.

    Returns:
        HttpResponse: Página renderizada con la lista de papers.
    """
    update_info = None
    try:
        api_url = f"https://api.github.com/repos/{settings.GITHUB_REPO}/releases/latest"
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            latest_version = data.get('tag_name')
            if latest_version and latest_version != settings.CURRENT_VERSION:
                update_info = {
                    'version': latest_version,
                    'url': data.get('html_url')
                }
    except requests.RequestException:
        print("Advertencia: No se pudo conectar a la API de GitHub para verificar actualizaciones.")

    papers_query = Paper.objects.select_related(
        'edicion__revista',
        'estatus_publicacion',
        'programa'
    ).prefetch_related(
        Prefetch(
            'paperautor_set',
            queryset=PaperAutor.objects.select_related('autor').order_by('orden_autor'),
            to_attr='autores_ordenados'
        )
    )

    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    year_filter = request.GET.get('year', '')

    try:
        status_filter_int = int(status_filter) if status_filter else None
    except ValueError:
        status_filter_int = None

    try:
        year_filter_int = int(year_filter) if year_filter else None
    except ValueError:
        year_filter_int = None

    if search_query:
        papers_query = papers_query.filter(
            Q(titulo__icontains=search_query) |
            Q(doi__icontains=search_query) |
            Q(edicion__revista__nombre__icontains=search_query)
        )
    if status_filter_int:
        papers_query = papers_query.filter(estatus_publicacion__id=status_filter_int)
    if year_filter_int:
        papers_query = papers_query.filter(anio_publicacion=year_filter_int)

    papers_query = papers_query.order_by('-anio_publicacion', '-fecha_creacion')

    paginator = Paginator(papers_query, 10)
    page_number = request.GET.get('page')
    papers = paginator.get_page(page_number)

    status_list = EstatusPublicacion.objects.all().order_by('estatus')
    years_list = Paper.objects.values_list('anio_publicacion', flat=True).distinct().order_by('-anio_publicacion')

    context = {
        'papers': papers,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_filter_int': status_filter_int,
        'year_filter': year_filter,
        'year_filter_int': year_filter_int,
        'status_list': status_list,
        'years_list': years_list,
        'total_papers': papers_query.count(),
        'palabras_clave_json': json.dumps(list(PalabraClave.objects.all().values('id', 'nombre')))
    }

    return render(request, 'publications/paper_list_template.html', context)


@require_http_methods(["GET"])
def get_palabras_clave(request):
    """
    Devuelve todas las palabras clave existentes en formato JSON.

    Args:
        request (HttpRequest): Solicitud GET.

    Returns:
        JsonResponse: Lista de palabras clave o error.
    """
    try:
        palabras = PalabraClave.objects.all().values('id', 'nombre')
        return JsonResponse({'success': True, 'palabras_clave': list(palabras)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def get_new_paper_modal_content(request):
    """
    Renderiza el contenido dinámico del modal para crear un nuevo Paper.

    Incluye catálogos como estatus, revistas, autores, roles, programas y ejes SECITI/SECITHI.

    Args:
        request (HttpRequest): Solicitud GET que puede incluir IDs de nuevas entidades.

    Returns:
        HttpResponse: Template renderizado con los catálogos del formulario.
    """
    nuevo_autor_id = request.GET.get('nuevo_autor_id')
    nuevo_programa_id = request.GET.get('nuevo_programa_id')
    nuevo_eje_id = request.GET.get('nuevo_eje_id')

    estatus_publicaciones = EstatusPublicacion.objects.all()
    revistas = Revista.objects.all()
    roles = Rol.objects.all()
    autores = Autor.objects.all()
    programas_seciti = ProgramaSeciti.objects.all()
    ejes_secithi = EjeSecithi.objects.all()

    if nuevo_autor_id:
        try:
            nuevo_autor = Autor.objects.get(id=nuevo_autor_id)
            if not autores.filter(id=nuevo_autor_id).exists():
                autores = Autor.objects.all()
        except Autor.DoesNotExist:
            pass
    if nuevo_programa_id:
        try:
            nuevo_programa = ProgramaSeciti.objects.get(id=nuevo_programa_id)
            if not programas_seciti.filter(id=nuevo_programa_id).exists():
                programas_seciti = ProgramaSeciti.objects.all()
        except ProgramaSeciti.DoesNotExist:
            pass
    if nuevo_eje_id:
        try:
            nuevo_eje = EjeSecithi.objects.get(id=nuevo_eje_id)
            if not ejes_secithi.filter(id=nuevo_eje_id).exists():
                ejes_secithi = EjeSecithi.objects.all()
        except EjeSecithi.DoesNotExist:
            pass

    context = {
        'estatus_publicaciones': estatus_publicaciones,
        'programas_seciti': programas_seciti,
        'ejes_secithi': ejes_secithi,
        'revistas': revistas,
        'autores': autores,
        'roles_json': json.dumps(list(roles.values('id', 'nombre_rol', 'descripcion'))),
    }

    return render(request, 'modals/paper_accordion.html', context)
