from django.urls import path
from . import views

app_name = 'journals'

urlpatterns = [
    # ... otras URLs
    path('modal/new-journal/', views.modal_nueva_revista, name='modal_nueva_revista'),
    path('create/', views.guardar_revista, name='guardar_revista'),
    path('modal/new-country/', views.modal_nuevo_pais, name='modal_nuevo_pais'),
    path('modal/new-category/', views.modal_nueva_categoria, name='modal_nueva_categoria'),
    path('modal/new-scope/', views.modal_nuevo_ambito, name='modal_nuevo_ambito'),
    path('modal/new-publisher/',views.modal_nueva_editorial,name='modal_nueva_editorial'),
    path('create-country/', views.guardar_pais, name='guardar_pais'),
    path('create-category/', views.guardar_categoria, name='guardar_categoria'),
    path('create-scope/', views.guardar_ambito, name='guardar_ambito'),
    path('create-publisher/',views.guardar_editorial,name='guardar_editorial'),
    path('api/verificar-edicion/', views.verificar_edicion, name='verificar_edicion'),
]