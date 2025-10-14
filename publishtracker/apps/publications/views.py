# paper_list_view/views.py
import os
import json

from django.http import JsonResponse
from django.shortcuts import render
from django.db import transaction
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator
from django.core.files.storage import default_storage
from django.views.decorators.http import require_http_methods

from publications.models import Paper
from authors.models import PaperAutor, Rol, Autor, RolAutor
from .models import ArchivoPaper, PalabraClave, PaperPalabraClave, TipoArchivoPaper
from core.models import EstatusPublicacion, ProgramaSeciti, EjeSecithi
from journals.models import ArchivoRevista, Revista, EdicionRevista, TipoArchivoRevista
@require_http_methods(["POST"])
def create_paper(request):
    """
    Vista refactorizada para crear un Paper y todas sus relaciones de forma atómica.
    Maneja la persistencia de archivos para EdicionRevista y para Paper
    a través de sus respectivas tablas intermedias.
    """
    try:
        # transaction.atomic asegura que todas las operaciones de BD se completen
        # con éxito, o ninguna lo hará, evitando datos corruptos.
        with transaction.atomic():
            
            # --- PASO 1: OBTENER O CREAR LA EDICIÓN DE LA REVISTA ---
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

            # --- PASO 2: PROCESAR Y GUARDAR ARCHIVOS DE LA EDICIÓN ---
            tipos_archivo_revista_map = {
                'archivo_edicion_portada': 'Portada',
                'archivo_edicion_hoja_legal': 'Hoja Legal',
                'archivo_edicion_indice_de_paper': 'Indice de Paper',
            }
            for field_name, tipo_nombre in tipos_archivo_revista_map.items():
                if field_name in request.FILES:
                    tipo_obj = TipoArchivoRevista.objects.get(tipo=tipo_nombre)
                    # Usamos update_or_create para asegurar que el archivo se guarde
                    # tanto en registros nuevos como en existentes.
                    ArchivoRevista.objects.update_or_create(
                        edicion=edicion,
                        tipo_archivo=tipo_obj,
                        defaults={
                            'archivo': request.FILES[field_name],
                            'nombre_archivo': request.FILES[field_name].name
                        }
                    )

            # --- PASO 3: PREPARAR DATOS Y CREAR EL OBJETO PAPER ---
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
            # Directorio de destino para los archivos clonados
            clone_dir = os.path.join(str(edicion.anio), str(revista.id), str(paper.id), 'archivos_revista')

            # Obtener todos los archivos asociados a la edición que acabamos de guardar
            archivos_de_la_edicion = ArchivoRevista.objects.filter(edicion=edicion)

            for archivo_revista in archivos_de_la_edicion:
                # El nombre del archivo tal como se guardó en el disco
                nombre_archivo_guardado = os.path.basename(archivo_revista.archivo.name)

                # Ruta completa de destino
                destination_path = os.path.join(clone_dir, nombre_archivo_guardado)

                # Abrir el archivo original en modo lectura binaria ('rb') y guardarlo en el nuevo destino
                with archivo_revista.archivo.open('rb') as original_file:
                    default_storage.save(destination_path, original_file)

            # --- PASO 4: PROCESAR Y GUARDAR ARCHIVOS DEL PAPER ---
            tipos_archivo_paper_map = {
                'archivo_paper': 'Paper Completo',    # name del input -> tipo en la BD
                'primera_pagina': 'Primera Pagina', # name del input -> tipo en la BD
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

            # --- PASO 5: PROCESAR AUTORES Y PALABRAS CLAVE ---
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
            
            # Si todo ha ido bien, se llega aquí y la transacción se confirma.
            return JsonResponse({
                'success': True,
                'message': 'Paper y todos sus archivos han sido guardados exitosamente.',
                'paper_id': paper.id
            })

    except (ValueError, KeyError, json.JSONDecodeError) as e:
        # Errores de datos faltantes o mal formados
        return JsonResponse({'success': False, 'message': f'Error en los datos enviados: {str(e)}'}, status=400)
    except Exception as e:
        # Otros errores (ej. objeto no encontrado en la BD, error de guardado)
        import traceback
        traceback.print_exc() # Imprime el error completo en la consola del servidor
        return JsonResponse({'success': False, 'message': f'Ha ocurrido un error inesperado: {str(e)}'}, status=500)

@require_http_methods(["POST"])
def create_keywords(request):
    """
    Vista para crear una nueva palabra clave.
    Espera recibir el nombre de la palabra clave en el cuerpo de la petición JSON.
    
    Returns:
        JsonResponse con:
        - success: bool indicando si la operación fue exitosa
        - palabra_clave: objeto con la palabra clave creada (id y nombre)
        - message: mensaje descriptivo del resultado
    """
    try:
        data = json.loads(request.body)
        nombre = data.get('nombre', '').strip().lower()
        
        if not nombre:
            return JsonResponse({
                'success': False,
                'message': 'El nombre de la palabra clave es requerido'
            }, status=400)

        # Verificar si ya existe (case insensitive)
        palabra_existente = PalabraClave.objects.filter(
            nombre__iexact=nombre
        ).first()

        if palabra_existente:
            return JsonResponse({
                'success': True,
                'palabra_clave': {
                    'id': palabra_existente.id,
                    'nombre': palabra_existente.nombre
                },
                'message': 'La palabra clave ya existe'
            })

        # Crear nueva palabra clave
        palabra_nueva = PalabraClave.objects.create(nombre=nombre)
        
        return JsonResponse({
            'success': True,
            'palabra_clave': {
                'id': palabra_nueva.id,
                'nombre': palabra_nueva.nombre
            },
            'message': 'Palabra clave creada exitosamente'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Error al decodificar JSON'
        }, status=400)
        
    except Exception as e:
        # Registrar el error para debugging
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
    Vista para mostrar la lista de papers con filtros y paginación
    """
    # Query base con optimizaciones
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
    
    # Filtros
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    year_filter = request.GET.get('year', '')
    
    # Convertir status_filter a entero para comparación
    status_filter_int = None
    if status_filter:
        try:
            status_filter_int = int(status_filter)
        except ValueError:
            status_filter_int = None
    
    # Convertir year_filter a entero
    year_filter_int = None
    if year_filter:
        try:
            year_filter_int = int(year_filter)
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
    
    # Ordenamiento
    papers_query = papers_query.order_by('-anio_publicacion', '-fecha_creacion')
    
    # Paginación
    paginator = Paginator(papers_query, 10)
    page_number = request.GET.get('page')
    papers = paginator.get_page(page_number)
    
    # Datos adicionales para filtros
    from core.models import EstatusPublicacion
    status_list = EstatusPublicacion.objects.all().order_by('estatus')
    years_list = Paper.objects.values_list('anio_publicacion', flat=True).distinct().order_by('-anio_publicacion')
    
    context = {
        'papers': papers,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_filter_int': status_filter_int,  # Agregar versión convertida
        'year_filter': year_filter,
        'year_filter_int': year_filter_int,      # Agregar versión convertida
        'status_list': status_list,
        'years_list': years_list,
        'total_papers': papers_query.count(),
        'palabras_clave_json': json.dumps(list(PalabraClave.objects.all().values('id', 'nombre')))
    }
    
    return render(request, 'publications/paper_list_template.html', context)
@require_http_methods(["GET"])
def get_palabras_clave(request):
    """API para obtener todas las palabras clave disponibles"""
    try:
        palabras = PalabraClave.objects.all().values('id', 'nombre')
        palabras_list = list(palabras)
        return JsonResponse({'success': True, 'palabras_clave': palabras_list})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
def get_new_paper_modal_content(request):
    """
    Vista para renderizar el contenido del modal acordeón para un nuevo paper.
    """
    # Obtener IDs de entidades recién creadas desde la solicitud GET
    nuevo_autor_id = request.GET.get('nuevo_autor_id')
    nuevo_programa_id = request.GET.get('nuevo_programa_id') # <-- Nuevo parámetro
    nuevo_eje_id = request.GET.get('nuevo_eje_id')           # <-- Nuevo parámetro

    # Obtener las listas iniciales
    estatus_publicaciones = EstatusPublicacion.objects.all()
    revistas = Revista.objects.all()
    roles = Rol.objects.all()
    autores = Autor.objects.all() # <-- Asegurar que se incluya el nuevo autor si se creó

    # Obtener programas y ejes iniciales
    programas_seciti = ProgramaSeciti.objects.all() 
    ejes_secithi = EjeSecithi.objects.all()        

    # Si hay un ID de autor nuevo, asegurarse de que esté incluido
    if nuevo_autor_id:
        try:
            nuevo_autor = Autor.objects.get(id=nuevo_autor_id)
            if not autores.filter(id=nuevo_autor_id).exists():
                autores = Autor.objects.all() # Recargar la lista completa para incluir el nuevo
        except Autor.DoesNotExist:
            pass
    if nuevo_programa_id:
        try:
            nuevo_programa = ProgramaSeciti.objects.get(id=nuevo_programa_id)
            if not programas_seciti.filter(id=nuevo_programa_id).exists():
                programas_seciti = ProgramaSeciti.objects.all() # Recargar la lista completa
        except ProgramaSeciti.DoesNotExist:
            pass # Manejar error si el ID no existe
    if nuevo_eje_id:
        try:
            nuevo_eje = EjeSecithi.objects.get(id=nuevo_eje_id)
            if not ejes_secithi.filter(id=nuevo_eje_id).exists():
                ejes_secithi = EjeSecithi.objects.all() # Recargar la lista completa
        except EjeSecithi.DoesNotExist:
            pass # Manejar error si el ID no existe

    context = {
        'estatus_publicaciones': estatus_publicaciones,
        # Asegurarse de que las listas incluyan las nuevas entidades
        'programas_seciti': programas_seciti, # <-- Ahora puede incluir el nuevo
        'ejes_secithi': ejes_secithi,         # <-- Ahora puede incluir el nuevo
        'revistas': revistas,
        'autores': autores, # <-- Ahora puede incluir el nuevo
        'roles_json': json.dumps(list(roles.values('id', 'nombre_rol', 'descripcion'))),
    }
    return render(request, 'modals/paper_accordion.html', context)
