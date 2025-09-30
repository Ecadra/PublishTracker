# authors/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/search/', views.search_authors, name='search_authors'),
    path('api/roles/', views.get_roles, name='get_roles'),
    path('modal/new-author/', views.modal_nuevo_autor, name='modal_nuevo_autor'),
    path('create/', views.guardar_autor, name='guardar_autor'),
]