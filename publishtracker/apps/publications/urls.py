# publications/urls.py
from django.urls import path
from .views import paper_list_view, get_palabras_clave

app_name = "publications"

urlpatterns = [
    path("", paper_list_view, name="mis papers"),
    path('api/palabras-clave/', get_palabras_clave, name='get_palabras_clave'),
]
