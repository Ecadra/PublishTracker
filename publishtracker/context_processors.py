# publishtracker/context_processors.py
from publishtracker.utils.version_checker import check_for_updates


def update_checker(request):
    """
    Context processor que verifica actualizaciones de la aplicación.
    
    Returns:
        dict: Diccionario con información de actualización (si existe).
    """
    update_info = check_for_updates()
    
    return {
        'update_info': update_info
    }