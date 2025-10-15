# journals/views.py
from django.shortcuts import render
from django.http import JsonResponse
from .forms import AmbitoRevistaForm, CategoriaRevistaForm, EditorialForm, PaisForm, RevistaForm
from .models import ArchivoRevista, EdicionRevista, Editorial, CategoriaRevista, AmbitoRevista
from core.models import Pais

def modal_nueva_revista(request):
    # Obtener IDs de entidades recién creadas desde la solicitud GET
    nuevo_pais_id = request.GET.get('nuevo_pais_id')
    nueva_categoria_id = request.GET.get('nueva_categoria_id')
    nuevo_ambito_id = request.GET.get('nuevo_ambito_id')
    nueva_editorial_id = request.GET.get('nueva_editorial_id') # <-- Nuevo parámetro

    form = RevistaForm()

    # Obtener las listas iniciales
    editoriales = Editorial.objects.all() # <-- Cambio aquí
    categorias = CategoriaRevista.objects.all()
    ambitos = AmbitoRevista.objects.all()
    paises = Pais.objects.all()

    # Si hay IDs de entidades nuevas, añadirlos a las listas
    # Opcional: Si los modelos tienen un campo activo, filtrar aquí
    if nuevo_pais_id:
        try:
            nuevo_pais = Pais.objects.get(id=nuevo_pais_id)
            if not paises.filter(id=nuevo_pais_id).exists():
                paises = list(paises) + [nuevo_pais]
        except Pais.DoesNotExist:
            pass

    if nueva_categoria_id:
        try:
            nueva_categoria = CategoriaRevista.objects.get(id=nueva_categoria_id)
            if not categorias.filter(id=nueva_categoria_id).exists():
                categorias = list(categorias) + [nueva_categoria]
        except CategoriaRevista.DoesNotExist:
            pass

    if nuevo_ambito_id:
        try:
            nuevo_ambito = AmbitoRevista.objects.get(id=nuevo_ambito_id)
            if not ambitos.filter(id=nuevo_ambito_id).exists():
                ambitos = list(ambitos) + [nuevo_ambito]
        except AmbitoRevista.DoesNotExist:
            pass

    # <-- Nuevo bloque para editorial -->
    if nueva_editorial_id:
        try:
            nueva_editorial = Editorial.objects.get(id=nueva_editorial_id)
            if not editoriales.filter(id=nueva_editorial_id).exists():
                editoriales = list(editoriales) + [nueva_editorial]
        except Editorial.DoesNotExist:
            pass
    # <-- Fin nuevo bloque -->

    context = {
        'form': form,
        'editoriales': editoriales, # <-- Asegúrate de pasar la lista actualizada
        'categorias': categorias,
        'ambitos': ambitos,
        'paises': paises,
        # Asegúrate de pasar también los JSON si se usan en JS para otras cosas
        # 'editoriales_json': json.dumps(list(editoriales.values('id', 'nombre'))),
        # 'categorias_json': json.dumps(list(categorias.values('id', 'nombre'))),
        # 'ambitos_json': json.dumps(list(ambitos.values('id', 'nombre'))),
        # 'paises_json': json.dumps(list(paises.values('id', 'nombre', 'nombre_completo'))),
    }
    return render(request, 'modals/nueva_revista_form.html', context)
def guardar_revista(request):
    if request.method == 'POST':
        form = RevistaForm(request.POST)
        if form.is_valid():
            nueva_revista = form.save() # Guarda la revista
            # Devuelve éxito con datos de la nueva revista
            return JsonResponse({
                'success': True,
                'message': 'Revista guardada correctamente.',
                'objeto': {
                    'id': nueva_revista.id,
                    'nombre': nueva_revista.nombre,
                    'issn_principal': nueva_revista.issn_principal,
                }
            })
        else:
            # --- CAMBIO AQUÍ ---
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
            # ---
    else:
        return JsonResponse({'success': False, 'message': 'Método no permitido.'})
def modal_nuevo_pais(request):
    form = PaisForm()
    context = {
        'form': form,
        'titulo_modal': 'Añadir Nuevo País',
        'accion_guardar': 'guardarPais' # Nombre de la función JS para guardar
    }
    return render(request, 'modals/formulario_generico.html', context)

def modal_nueva_categoria(request):
    form = CategoriaRevistaForm()
    context = {
        'form': form,
        'titulo_modal': 'Añadir Nueva Categoría de Revista',
        'accion_guardar': 'guardarCategoria' # Nombre de la función JS para guardar
    }
    return render(request, 'modals/formulario_generico.html', context)

def modal_nuevo_ambito(request):
    form = AmbitoRevistaForm()
    context = {
        'form': form,
        'titulo_modal': 'Añadir Nuevo Ámbito de Revista',
        'accion_guardar': 'guardarAmbito' # Nombre de la función JS para guardar
    }
    return render(request, 'modals/formulario_generico.html', context)

# --- Vistas para guardar ---
def guardar_pais(request):
    if request.method == 'POST':
        form = PaisForm(request.POST)
        if form.is_valid():
            nuevo_pais = form.save()
            return JsonResponse({
                'success': True,
                'message': 'País guardado correctamente.',
                'objeto': {
                    'id': nuevo_pais.id,
                    'nombre': nuevo_pais.nombre, # <-- Nombre simple
                    'nombre_completo': nuevo_pais.nombre_completo, # <-- Nombre completo con código ISO
                    'codigo_iso': nuevo_pais.codigo_iso, # <-- Código ISO (opcional, pero bueno tenerlo)
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
def guardar_categoria(request):
    if request.method == 'POST':
        form = CategoriaRevistaForm(request.POST)
        if form.is_valid():
            nueva_categoria = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Categoría guardada correctamente.',
                'objeto': {
                    'id': nueva_categoria.id,
                    'nombre': nueva_categoria.nombre,
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

def guardar_ambito(request):
    if request.method == 'POST':
        form = AmbitoRevistaForm(request.POST)
        if form.is_valid():
            nuevo_ambito = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Ámbito guardado correctamente.',
                'objeto': {
                    'id': nuevo_ambito.id,
                    'nombre': nuevo_ambito.nombre,
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
def modal_nueva_editorial(request):
    form = EditorialForm()
    context = {
        'form': form,
        'titulo_modal': 'Añadir Nueva Editorial',
        'accion_guardar': 'guardarEditorial', # Nombre de la función JS para guardar
        # Asegurarse de que el contexto incluya los países para el select
        'paises': Pais.objects.all(), # Asegúrate de pasar las opciones necesarias
    }
    return render(request, 'modals/formulario_generico.html', context)

def guardar_editorial(request):
    if request.method == 'POST':
        form = EditorialForm(request.POST)
        if form.is_valid():
            nueva_editorial = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Editorial guardada correctamente.',
                'objeto': {
                    'id': nueva_editorial.id,
                    'nombre': nueva_editorial.nombre,
                    # Opcional: puedes incluir otras propiedades como nombre_completo
                    # 'nombre_completo': nueva_editorial.nombre_completo,
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
def verificar_edicion(request):
    revista_id = request.GET.get('revista_id')
    anio = request.GET.get('anio')
    volumen = request.GET.get('volumen')
    numero = request.GET.get('numero')

    if not all([revista_id, anio, volumen, numero]):
        return JsonResponse({'success': False, 'error': 'Parámetros incompletos'}, status=400)

    try:
        # Buscamos la edición
        edicion = EdicionRevista.objects.get(
            revista_id=revista_id,
            anio=anio,
            volumen=volumen,
            numero=numero
        )
        
        # Obtenemos los archivos que ya existen para esta edición
        archivos_existentes = ArchivoRevista.objects.filter(edicion=edicion).select_related('tipo_archivo')
        
        # Creamos un diccionario para un acceso fácil en el frontend
        archivos = {
            archivo.tipo_archivo.tipo: {
                'nombre': archivo.nombre_archivo,
                'url': archivo.archivo.url
            }
            for archivo in archivos_existentes
        }

        return JsonResponse({
            'success': True,
            'edicion_existe': True,
            'archivos': archivos  # Devolvemos el diccionario de archivos
        })

    except EdicionRevista.DoesNotExist:
        # Si la edición no existe, no hay archivos
        return JsonResponse({'success': True, 'edicion_existe': False, 'archivos': {}})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
