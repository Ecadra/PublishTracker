# authors/urls.py
from django.urls import path
from .views import search_authors, get_roles

urlpatterns = [
    path('api/search/', search_authors, name='search_authors'),
    path('api/roles/', get_roles, name='get_roles'),
]