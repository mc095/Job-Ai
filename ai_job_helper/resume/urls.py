from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='resume_home'),
    path('save/<str:section>/', views.save_section, name='save_section'),
    path('compile/', views.compile_resume, name='compile_resume'),
    path('data/', views.get_resume_data, name='get_resume_data'),
]