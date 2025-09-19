from django.urls import path
from .views import get_new_paper_modal_content

app_name = 'core'

urlpatterns = [

    path('modal/new-paper/', get_new_paper_modal_content, name='modal_new_paper_content'),
]