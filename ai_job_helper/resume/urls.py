from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='resume_home'),
    path('save-to-profile/', views.save_resume_to_profile, name='save_resume_to_profile'),
]