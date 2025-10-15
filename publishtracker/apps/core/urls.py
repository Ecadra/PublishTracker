from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('modal/new-program/', views.modal_nuevo_programa, name='modal_nuevo_programa'),
    path('modal/new-axis/', views.modal_nuevo_eje, name='modal_nuevo_eje'),
    path('create-program/', views.guardar_programa, name='guardar_programa'),
    path('create-axis/', views.guardar_eje, name='guardar_eje'),
    path('apply-update/', views.apply_update, name='apply_update'),
]