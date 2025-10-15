# paper_list_view/views.py
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

from publications.models import Paper
from authors.models import Rol, Autor, RolAutor
from publications.models import PaperAutor
from .models import ArchivoPaper, PalabraClave, PaperPalabraClave, TipoArchivoPaper
from core.models import EstatusPublicacion, ProgramaSeciti, EjeSecithi
from journals.models import ArchivoRevista, Revista, EdicionRevista, TipoArchivoRevista


@require_http_methods(["POST"])
def create_paper(request):
    """
    Crear un Paper y sus relaciones de forma atómica.
    Pasos:
    1. Validar revista y obtener/crear edición
    2. Guardar archivos de la edición (portada, hoja legal, índice)
    3. Validar estatus y crear el Paper
    4. Clonar archivos de la edición al directorio del Paper
    5. Guardar archivos propios del Paper (PDF, primera página)
    6. Registrar autores con su rol y orden
    7. Registrar palabras clave (crear si no existen)
    8. Retornar respuesta exitosa
    """
    try:
        # 1. Validar revista y obtener/crear edición
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

            # 2. Guardar archivos de la edición (portada, hoja legal, índice)
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

            # 3. Validar estatus y crear el Paper
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

            # 4. Clonar archivos de la edición al directorio del Paper
            clone_dir = os.path.join(str(edicion.anio), str(revista.id), str(paper.id), 'archivos_revista')
            archivos_de_la_edicion = ArchivoRevista.objects.filter(edicion=edicion)
            for archivo_revista in archivos_de_la_edicion:
                nombre_archivo_guardado = os.path.basename(archivo_revista.archivo.name)
                destination_path = os.path.join(clone_dir, nombre_archivo_guardado)
                with archivo_revista.archivo.open('rb') as original_file:
                    default_storage.save(destination_path, original_file)

            # 5. Guardar archivos propios del Paper (PDF, primera página)
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

            # 6. Registrar autores con su rol y orden
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

            # 7. Registrar palabras clave (crear si no existen)
            palabras_clave = json.loads(request.POST.get('palabras_clave', '[]'))
            for palabra_data in palabras_clave:
                palabra_obj, _ = PalabraClave.objects.get_or_create(
                    nombre=palabra_data['nombre'].strip().lower(),
                    defaults={'nombre': palabra_data['nombre'].strip()}
                )
                PaperPalabraClave.objects.create(paper=paper, palabra_clave=palabra_obj)

            # 8. Retornar respuesta exitosa
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
    Crear una nueva palabra clave (JSON).
    Pasos:
    1. Leer y validar nombre desde el cuerpo JSON
    2. Verificar existencia case-insensitive
    3. Retornar existente si ya está registrado
    4. Crear palabra clave y retornar datos
    5. Manejar errores de JSON y excepciones
    """
    try:
        # 1. Leer y validar nombre desde el cuerpo JSON
        data = json.loads(request.body)
        nombre = data.get('nombre', '').strip().lower()
        if not nombre:
            return JsonResponse({'success': False, 'message': 'El nombre de la palabra clave es requerido'}, status=400)

        # 2. Verificar existencia case-insensitive
        palabra_existente = PalabraClave.objects.filter(nombre__iexact=nombre).first()

        # 3. Retornar existente si ya está registrado
        if palabra_existente:
            return JsonResponse({
                'success': True,
                'palabra_clave': {'id': palabra_existente.id, 'nombre': palabra_existente.nombre},
                'message': 'La palabra clave ya existe'
            })

        # 4. Crear palabra clave y retornar datos
        palabra_nueva = PalabraClave.objects.create(nombre=nombre)
        return JsonResponse({
            'success': True,
            'palabra_clave': {'id': palabra_nueva.id, 'nombre': palabra_nueva.nombre},
            'message': 'Palabra clave creada exitosamente'
        })

    except json.JSONDecodeError:
        # 5. Manejar errores de JSON y excepciones
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
    Listar papers con filtros y paginación.
    Pasos:
    0. Buscar actualizaciones de releases con la API de github
    1. Construir query base optimizada (select_related/prefetch)
    2. Leer filtros de búsqueda, estatus y año
    3. Convertir filtros a tipos adecuados
    4. Aplicar filtros al queryset
    5. Ordenar por año y fecha de creación
    6. Paginar resultados
    7. Preparar listas de filtros y datos extra
    8. Renderizar template con el contexto
    """
    #0. Buscar actualizaciones
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
        # Si hay un error de red (sin conexión, etc.), simplemente no se muestra la notificación.
        print("Advertencia: No se pudo conectar a la API de GitHub para verificar actualizaciones.")
    
    # 1. Construir query base optimizada (select_related/prefetch)
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

    # 2. Leer filtros de búsqueda, estatus y año
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    year_filter = request.GET.get('year', '')

    # 3. Convertir filtros a tipos adecuados
    status_filter_int = None
    if status_filter:
        try:
            status_filter_int = int(status_filter)
        except ValueError:
            status_filter_int = None

    year_filter_int = None
    if year_filter:
        try:
            year_filter_int = int(year_filter)
        except ValueError:
            year_filter_int = None

    # 4. Aplicar filtros al queryset
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

    # 5. Ordenar por año y fecha de creación
    papers_query = papers_query.order_by('-anio_publicacion', '-fecha_creacion')

    # 6. Paginar resultados
    paginator = Paginator(papers_query, 10)
    page_number = request.GET.get('page')
    papers = paginator.get_page(page_number)

    # 7. Preparar listas de filtros y datos extra
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

    # 8. Renderizar template con el contexto
    return render(request, 'publications/paper_list_template.html', context)


@require_http_methods(["GET"])
def get_palabras_clave(request):
    """
    Obtener todas las palabras clave.
    Pasos:
    1. Consultar todas las palabras clave
    2. Convertir a lista serializable
    3. Retornar JsonResponse con éxito
    4. Manejar errores con status 500
    """
    try:
        # 1. Consultar todas las palabras clave
        palabras = PalabraClave.objects.all().values('id', 'nombre')

        # 2. Convertir a lista serializable
        palabras_list = list(palabras)

        # 3. Retornar JsonResponse con éxito
        return JsonResponse({'success': True, 'palabras_clave': palabras_list})
    except Exception as e:
        # 4. Manejar errores con status 500
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def get_new_paper_modal_content(request):
    """
    Renderizar el contenido del modal para crear Paper.
    Pasos:
    1. Leer IDs de entidades recién creadas desde GET
    2. Consultar catálogos base (estatus, revistas, roles, autores)
    3. Consultar programas y ejes SECITI/SECITHI
    4. Asegurar inclusión de nuevas entidades si aplican
    5. Construir contexto con catálogos y roles en JSON
    6. Renderizar template del acordeón
    """
    # 1. Leer IDs de entidades recién creadas desde GET
    nuevo_autor_id = request.GET.get('nuevo_autor_id')
    nuevo_programa_id = request.GET.get('nuevo_programa_id')
    nuevo_eje_id = request.GET.get('nuevo_eje_id')

    # 2. Consultar catálogos base (estatus, revistas, roles, autores)
    estatus_publicaciones = EstatusPublicacion.objects.all()
    revistas = Revista.objects.all()
    roles = Rol.objects.all()
    autores = Autor.objects.all()

    # 3. Consultar programas y ejes SECITI/SECITHI
    programas_seciti = ProgramaSeciti.objects.all()
    ejes_secithi = EjeSecithi.objects.all()

    # 4. Asegurar inclusión de nuevas entidades si aplican
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

    # 5. Construir contexto con catálogos y roles en JSON
    context = {
        'estatus_publicaciones': estatus_publicaciones,
        'programas_seciti': programas_seciti,
        'ejes_secithi': ejes_secithi,
        'revistas': revistas,
        'autores': autores,
        'roles_json': json.dumps(list(roles.values('id', 'nombre_rol', 'descripcion'))),
    }

    # 6. Renderizar template del acordeón
    return render(request, 'modals/paper_accordion.html', context)
