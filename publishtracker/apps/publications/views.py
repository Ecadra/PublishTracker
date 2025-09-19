# paper_list_view/views.py
from django.shortcuts import render
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator
from django.http import JsonResponse
from publications.models import Paper
from authors.models import PaperAutor, Autor

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
        'total_papers': papers_query.count()
    }
    
    return render(request, 'publications/paper_list_template.html', context)