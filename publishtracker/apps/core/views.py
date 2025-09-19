import json
from django.shortcuts import render

from django.shortcuts import render
from core.models import EstatusPublicacion, ProgramaSeciti, EjeSecithi
from journals.models import Revista
from authors.models import Autor, Rol  # Asumiendo que tienes un modelo Autor

def get_new_paper_modal_content(request):
    """
    Vista para renderizar el contenido del modal acordeón para un nuevo paper.
    """
    context = {
        'estatus_publicaciones': EstatusPublicacion.objects.all(),
        'programas_seciti': ProgramaSeciti.objects.all(),
        'ejes_secithi': EjeSecithi.objects.all(),
        'revistas': Revista.objects.all(),  # Para el paso de selección de revista
        'autores': Autor.objects.all()[:10], # Carga inicial de autores (puedes paginar o buscar vía AJAX)
        'roles_json': json.dumps(list(Rol.objects.all().values('id', 'nombre_rol', 'descripcion')))
    }
    print("Contexto para el modal de paper:", context)  # Depuración
    return render(request, 'modals/paper_accordion.html', context)

