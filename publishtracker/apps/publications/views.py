# paper_list_view/views.py
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator
from publications.models import Paper
from authors.models import PaperAutor, Rol, Autor
from .models import PalabraClave, PaperPalabraClave
from core.models import EstatusPublicacion, ProgramaSeciti, EjeSecithi
from journals.models import Revista, EdicionRevista
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.db import transaction

@require_http_methods(["POST"])
def create_paper(request):
    """
    Vista para crear un nuevo paper con todas sus relaciones.
    Maneja la creación del paper, sus autores, palabras clave y archivos adjuntos.
    AHORA INCLUYE EL CAMPO 'proposito'.
    """
    try:
        with transaction.atomic():
            # Obtener instancias de los modelos relacionados
            estatus_id = request.POST.get('estatus_publicacion')
            revista_id = request.POST.get('revista')
            print(estatus_id)
            print(revista_id)
            # Obtener o crear la edición de revista
            revista = Revista.objects.get(id=revista_id) if revista_id else None
            if not revista:
                raise ValueError("La revista es requerida")
                
            # Crear o obtener la edición de la revista
            volumen = request.POST.get('volumen')
            numero = request.POST.get('numero')
            anio = request.POST.get('anio_publicacion')
            
            edicion = EdicionRevista.objects.filter(
                revista=revista,
                anio=anio,
                volumen=volumen,
                numero=numero
            ).first()
            
            if not edicion:
                edicion = EdicionRevista.objects.create(
                    revista=revista,
                    anio=anio,
                    volumen=volumen,
                    numero=numero,
                    indice_revista=request.POST.get('indice_revista')
                )
            
            # Obtener otros modelos relacionados
            estatus = EstatusPublicacion.objects.get(id=estatus_id) if estatus_id else None
            if not estatus:
                raise ValueError("El estatus de publicación es requerido")
             # --- IMPRIMIR VALORES CRÍTICOS ---
            recibio_apoyo_seciti_str = request.POST.get('recibio_apoyo_seciti', 'false') # Valor por defecto para depuración
            print("Debug - recibio_apoyo_seciti (raw):", repr(recibio_apoyo_seciti_str))
            recibio_apoyo_seciti_bool = recibio_apoyo_seciti_str == 'true'
            print("Debug - recibio_apoyo_seciti (evaluado):", recibio_apoyo_seciti_bool)

            programa_seciti_id = request.POST.get('programa_seciti')
            eje_secithi_id = request.POST.get('eje_secithi')
            print("Debug - programa_seciti_id:", repr(programa_seciti_id))
            print("Debug - eje_secithi_id:", repr(eje_secithi_id))
            # --- FIN IMPRESIÓN ---
            # Extraer datos básicos del paper
            # --- NUEVO: Incluir 'proposito' en la recolección de datos ---
            data = {
                'titulo': request.POST.get('titulo'),
                'anio_publicacion': anio,
                'estatus_publicacion': estatus,
                'edicion': edicion,
                'recibio_apoyo_seciti': request.POST.get('recibio_apoyo_seciti') == 'true',
                'doi': request.POST.get('doi'),
                'url_cita': request.POST.get('url_cita'),
                'total_citas': request.POST.get('total_citas') or 0,
                'pagina_inicio': request.POST.get('pagina_inicio'),
                'pagina_fin': request.POST.get('pagina_fin'),
                'objetivo': request.POST.get('objetivo'),
                'descripcion': request.POST.get('descripcion'),
                'abstract': request.POST.get('abstract'),
                'referencia_apa': request.POST.get('referencia_apa'),
                # Añadir el campo proposito aquí
                'proposito': request.POST.get('proposito'), # <-- Agregar esta línea
            }
            # --- FIN NUEVO ---

            # Agregar programa y eje si tiene apoyo SECITI
            print(data)
            if data['recibio_apoyo_seciti']:
                print('recibio apoyo')
                programa_id = request.POST.get('programa_seciti')
                eje_id = request.POST.get('eje_secithi')
                
                if not programa_id:
                    raise ValueError("Si el paper tiene apoyo SECITI, debe seleccionar un programa")
                if not eje_id:
                    raise ValueError("Si el paper tiene apoyo SECITI, debe seleccionar un eje")
                
                # Asegurarse de que las instancias existen
                try:
                    data['programa'] = ProgramaSeciti.objects.get(id=programa_id)
                except ProgramaSeciti.DoesNotExist:
                    raise ValueError(f"Programa SECITI con ID {programa_id} no encontrado.")
                try:
                    data['eje_secithi'] = EjeSecithi.objects.get(id=eje_id)
                except EjeSecithi.DoesNotExist:
                    raise ValueError(f"Eje SECITHI con ID {eje_id} no encontrado.")

            # Crear el paper
            paper = Paper.objects.create(**data) # <-- 'proposito', 'programa', 'eje_secithi' se asignan aquí si están en 'data'


            # Procesar autores
            autores = json.loads(request.POST.get('autores', '[]'))
            if not autores:
                raise ValueError("Debe seleccionar al menos un autor")

            # Crear las relaciones autor-paper
            for autor in autores:
                if not all(k in autor for k in ('autor_id', 'orden', 'rol_id')):
                    raise ValueError("Datos de autor incompletos")
                    
                from authors.models import RolAutor
                try:
                    rol_autor = RolAutor.objects.get(autor_id=autor['autor_id'], rol_id=autor['rol_id'])
                except RolAutor.DoesNotExist:
                    rol_autor = RolAutor.objects.create(
                        autor_id=autor['autor_id'],
                        rol_id=autor['rol_id']
                    )
                
                PaperAutor.objects.create(
                    paper=paper,
                    autor_id=autor['autor_id'],
                    orden_autor=autor['orden'],
                    rol_autor=rol_autor
                )

            # Procesar palabras clave
            palabras_clave = json.loads(request.POST.get('palabras_clave', '[]'))
            for palabra in palabras_clave:
                # Si la palabra clave es nueva (id es null), crearla primero
                if palabra.get('id') is None:
                    palabra_clave = PalabraClave.objects.create(nombre=palabra['nombre'])
                else:
                    palabra_clave = PalabraClave.objects.get(id=palabra['id'])
                
                # Crear la relación con el paper
                PaperPalabraClave.objects.create(
                    paper=paper,
                    palabra_clave=palabra_clave
                )

            # Procesar archivos
            if 'archivo_paper' in request.FILES:
                archivo = request.FILES['archivo_paper']
                ruta_archivo = f'papers/{paper.id}/{archivo.name}'
                paper.archivo_paper = default_storage.save(ruta_archivo, archivo)

            if 'primera_pagina' in request.FILES:
                archivo = request.FILES['primera_pagina']
                ruta_archivo = f'papers/{paper.id}/primera_pagina/{archivo.name}'
                paper.primera_pagina = default_storage.save(ruta_archivo, archivo)

            paper.save()

            return JsonResponse({
                'success': True,
                'message': 'Paper creado exitosamente',
                'paper_id': paper.id
            })

    except Exception as e:
        # Registrar el error para debugging
        import traceback
        print("Error al crear paper:", str(e))
        print(traceback.format_exc())
        
        return JsonResponse({
            'success': False,
            'message': f'Error al crear el paper: {str(e)}',
            'error_details': traceback.format_exc()
        }, status=500)
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
    programas_seciti = ProgramaSeciti.objects.all() # <-- Asegurar que se incluya el nuevo si se creó
    ejes_secithi = EjeSecithi.objects.all()         # <-- Asegurar que se incluya el nuevo si se creó

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
