from django.urls import path
from . import views

urlpatterns = [
    path("", views.training_home, name="training_home"),
    path("<str:session_id>/chat/", views.training_chat, name="training_chat"),
]
