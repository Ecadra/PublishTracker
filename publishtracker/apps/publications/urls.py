# publications/urls.py
from django.urls import path
from . import views

app_name = "publications"

urlpatterns = [
    path("", views.paper_list_view, name="mis papers"),
    path('api/palabras-clave/', views.get_palabras_clave, name='get_palabras_clave'),
    path('api/palabras-clave/create/', views.create_keywords,name="create keywords"),
    path('publications/create/', views.create_paper,name = 'create_paper'),
    path('modal/new-paper/', views.get_new_paper_modal_content, name='modal_new_paper_content'),
]
