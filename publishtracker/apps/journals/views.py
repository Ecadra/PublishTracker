# journals/views.py
from django.shortcuts import render
from django.http import JsonResponse
from .forms import AmbitoRevistaForm, CategoriaRevistaForm, EditorialForm, PaisForm, RevistaForm
from .models import ArchivoRevista, EdicionRevista, Editorial, CategoriaRevista, AmbitoRevista
from core.models import Pais


def modal_nueva_revista(request):
    """
    Renderizar el modal para crear una revista.
    Pasos:
    1. Leer IDs de entidades recién creadas desde GET
    2. Instanciar formulario base
    3. Obtener listas iniciales de catálogos
    4. Incorporar entidades nuevas a las listas si aplican
    5. Preparar contexto con formulario y catálogos
    6. Renderizar template del modal
    """
    # 1. Leer IDs de entidades recién creadas desde GET
    nuevo_pais_id = request.GET.get('nuevo_pais_id')
    nueva_categoria_id = request.GET.get('nueva_categoria_id')
    nuevo_ambito_id = request.GET.get('nuevo_ambito_id')
    nueva_editorial_id = request.GET.get('nueva_editorial_id')

    # 2. Instanciar formulario base
    form = RevistaForm()

    # 3. Obtener listas iniciales de catálogos
    editoriales = Editorial.objects.all()
    categorias = CategoriaRevista.objects.all()
    ambitos = AmbitoRevista.objects.all()
    paises = Pais.objects.all()

    # 4. Incorporar entidades nuevas a las listas si aplican
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

    if nueva_editorial_id:
        try:
            nueva_editorial = Editorial.objects.get(id=nueva_editorial_id)
            if not editoriales.filter(id=nueva_editorial_id).exists():
                editoriales = list(editoriales) + [nueva_editorial]
        except Editorial.DoesNotExist:
            pass

    # 5. Preparar contexto con formulario y catálogos
    context = {
        'form': form,
        'editoriales': editoriales,
        'categorias': categorias,
        'ambitos': ambitos,
        'paises': paises,
    }

    # 6. Renderizar template del modal
    return render(request, 'modals/nueva_revista_form.html', context)


def guardar_revista(request):
    """
    Guardar una revista desde el formulario.
    Pasos:
    1. Validar método HTTP POST
    2. Instanciar y validar formulario
    3. Guardar y retornar éxito con datos clave
    4. Construir y retornar errores de validación
    5. Retornar error por método no permitido
    """
    # 1. Validar método HTTP POST
    if request.method == 'POST':
        # 2. Instanciar y validar formulario
        form = RevistaForm(request.POST)
        if form.is_valid():
            # 3. Guardar y retornar éxito con datos clave
            nueva_revista = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Revista guardada correctamente.',
                'objeto': {
                    'id': nueva_revista.id,
                    'nombre': nueva_revista.nombre,
                    'issn_principal': nueva_revista.issn_principal,
                }
            })
        # 4. Construir y retornar errores de validación
        errors_dict = {field: [str(error) for error in error_list]
                       for field, error_list in form.errors.items()}
        return JsonResponse({
            'success': False,
            'message': 'Errores de validación en uno o más campos.',
            'errors': errors_dict
        })
    # 5. Retornar error por método no permitido
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})


def modal_nuevo_pais(request):
    """
    Renderizar el modal para crear un país.
    Pasos:
    1. Instanciar formulario
    2. Preparar contexto
    3. Renderizar template genérico
    """
    # 1. Instanciar formulario
    form = PaisForm()

    # 2. Preparar contexto
    context = {
        'form': form,
        'titulo_modal': 'Añadir Nuevo País',
        'accion_guardar': 'guardarPais',
    }

    # 3. Renderizar template genérico
    return render(request, 'modals/formulario_generico.html', context)


def modal_nueva_categoria(request):
    """
    Renderizar el modal para crear una categoría de revista.
    Pasos:
    1. Instanciar formulario
    2. Preparar contexto
    3. Renderizar template genérico
    """
    # 1. Instanciar formulario
    form = CategoriaRevistaForm()

    # 2. Preparar contexto
    context = {
        'form': form,
        'titulo_modal': 'Añadir Nueva Categoría de Revista',
        'accion_guardar': 'guardarCategoria',
    }

    # 3. Renderizar template genérico
    return render(request, 'modals/formulario_generico.html', context)


def modal_nuevo_ambito(request):
    """
    Renderizar el modal para crear un ámbito de revista.
    Pasos:
    1. Instanciar formulario
    2. Preparar contexto
    3. Renderizar template genérico
    """
    # 1. Instanciar formulario
    form = AmbitoRevistaForm()

    # 2. Preparar contexto
    context = {
        'form': form,
        'titulo_modal': 'Añadir Nuevo Ámbito de Revista',
        'accion_guardar': 'guardarAmbito',
    }

    # 3. Renderizar template genérico
    return render(request, 'modals/formulario_generico.html', context)


def guardar_pais(request):
    """
    Guardar un país desde el formulario.
    Pasos:
    1. Validar método HTTP POST
    2. Instanciar y validar formulario
    3. Guardar y retornar éxito con datos clave
    4. Construir y retornar errores de validación
    5. Retornar error por método no permitido
    """
    # 1. Validar método HTTP POST
    if request.method == 'POST':
        # 2. Instanciar y validar formulario
        form = PaisForm(request.POST)
        if form.is_valid():
            # 3. Guardar y retornar éxito con datos clave
            nuevo_pais = form.save()
            return JsonResponse({
                'success': True,
                'message': 'País guardado correctamente.',
                'objeto': {
                    'id': nuevo_pais.id,
                    'nombre': nuevo_pais.nombre,
                    'nombre_completo': nuevo_pais.nombre_completo,
                    'codigo_iso': nuevo_pais.codigo_iso,
                }
            })
        # 4. Construir y retornar errores de validación
        errors_dict = {field: [str(error) for error in error_list]
                       for field, error_list in form.errors.items()}
        return JsonResponse({
            'success': False,
            'message': 'Errores de validación en uno o más campos.',
            'errors': errors_dict
        })
    # 5. Retornar error por método no permitido
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})


def guardar_categoria(request):
    """
    Guardar una categoría de revista.
    Pasos:
    1. Validar método HTTP POST
    2. Instanciar y validar formulario
    3. Guardar y retornar éxito
    4. Construir y retornar errores de validación
    5. Retornar error por método no permitido
    """
    # 1. Validar método HTTP POST
    if request.method == 'POST':
        # 2. Instanciar y validar formulario
        form = CategoriaRevistaForm(request.POST)
        if form.is_valid():
            # 3. Guardar y retornar éxito
            nueva_categoria = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Categoría guardada correctamente.',
                'objeto': {
                    'id': nueva_categoria.id,
                    'nombre': nueva_categoria.nombre,
                }
            })
        # 4. Construir y retornar errores de validación
        errors_dict = {field: [str(error) for error in error_list]
                       for field, error_list in form.errors.items()}
        return JsonResponse({
            'success': False,
            'message': 'Errores de validación en uno o más campos.',
            'errors': errors_dict
        })
    # 5. Retornar error por método no permitido
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})


def guardar_ambito(request):
    """
    Guardar un ámbito de revista.
    Pasos:
    1. Validar método HTTP POST
    2. Instanciar y validar formulario
    3. Guardar y retornar éxito
    4. Construir y retornar errores de validación
    5. Retornar error por método no permitido
    """
    # 1. Validar método HTTP POST
    if request.method == 'POST':
        # 2. Instanciar y validar formulario
        form = AmbitoRevistaForm(request.POST)
        if form.is_valid():
            # 3. Guardar y retornar éxito
            nuevo_ambito = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Ámbito guardado correctamente.',
                'objeto': {
                    'id': nuevo_ambito.id,
                    'nombre': nuevo_ambito.nombre,
                }
            })
        # 4. Construir y retornar errores de validación
        errors_dict = {field: [str(error) for error in error_list]
                       for field, error_list in form.errors.items()}
        return JsonResponse({
            'success': False,
            'message': 'Errores de validación en uno o más campos.',
            'errors': errors_dict
        })
    # 5. Retornar error por método no permitido
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})


def modal_nueva_editorial(request):
    """
    Renderizar el modal para crear una editorial.
    Pasos:
    1. Instanciar formulario
    2. Preparar contexto incluyendo países
    3. Renderizar template genérico
    """
    # 1. Instanciar formulario
    form = EditorialForm()

    # 2. Preparar contexto incluyendo países
    context = {
        'form': form,
        'titulo_modal': 'Añadir Nueva Editorial',
        'accion_guardar': 'guardarEditorial',
        'paises': Pais.objects.all(),
    }

    # 3. Renderizar template genérico
    return render(request, 'modals/formulario_generico.html', context)


def guardar_editorial(request):
    """
    Guardar una editorial.
    Pasos:
    1. Validar método HTTP POST
    2. Instanciar y validar formulario
    3. Guardar y retornar éxito
    4. Construir y retornar errores de validación
    5. Retornar error por método no permitido
    """
    # 1. Validar método HTTP POST
    if request.method == 'POST':
        # 2. Instanciar y validar formulario
        form = EditorialForm(request.POST)
        if form.is_valid():
            # 3. Guardar y retornar éxito
            nueva_editorial = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Editorial guardada correctamente.',
                'objeto': {
                    'id': nueva_editorial.id,
                    'nombre': nueva_editorial.nombre,
                }
            })
        # 4. Construir y retornar errores de validación
        errors_dict = {field: [str(error) for error in error_list]
                       for field, error_list in form.errors.items()}
        return JsonResponse({
            'success': False,
            'message': 'Errores de validación en uno o más campos.',
            'errors': errors_dict
        })
    # 5. Retornar error por método no permitido
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})


def verificar_edicion(request):
    """
    Verificar existencia de edición y listar archivos asociados.
    Pasos:
    1. Leer parámetros requeridos desde GET
    2. Validar integridad de parámetros
    3. Consultar edición específica
    4. Consultar archivos existentes relacionados
    5. Construir diccionario {tipo: {nombre, url}}
    6. Retornar JSON con estado y archivos
    7. Manejar ausencia de edición
    8. Manejar errores inesperados
    """
    # 1. Leer parámetros requeridos desde GET
    revista_id = request.GET.get('revista_id')
    anio = request.GET.get('anio')
    volumen = request.GET.get('volumen')
    numero = request.GET.get('numero')

    # 2. Validar integridad de parámetros
    if not all([revista_id, anio, volumen, numero]):
        return JsonResponse({'success': False, 'error': 'Parámetros incompletos'}, status=400)

    try:
        # 3. Consultar edición específica
        edicion = EdicionRevista.objects.get(
            revista_id=revista_id,
            anio=anio,
            volumen=volumen,
            numero=numero
        )

        # 4. Consultar archivos existentes relacionados
        archivos_existentes = (
            ArchivoRevista.objects
            .filter(edicion=edicion)
            .select_related('tipo_archivo')
        )

        # 5. Construir diccionario {tipo: {nombre, url}}
        archivos = {
            archivo.tipo_archivo.tipo: {
                'nombre': archivo.nombre_archivo,
                'url': archivo.archivo.url
            }
            for archivo in archivos_existentes
        }

        # 6. Retornar JSON con estado y archivos
        return JsonResponse({
            'success': True,
            'edicion_existe': True,
            'archivos': archivos
        })

    except EdicionRevista.DoesNotExist:
        # 7. Manejar ausencia de edición
        return JsonResponse({'success': True, 'edicion_existe': False, 'archivos': {}})

    except Exception as e:
        # 8. Manejar errores inesperados
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
