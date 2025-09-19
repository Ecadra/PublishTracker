# publications/urls.py
from django.urls import path
from .views import paper_list_view

app_name = "publications"

urlpatterns = [
    path("", paper_list_view, name="mis papers"),
]
