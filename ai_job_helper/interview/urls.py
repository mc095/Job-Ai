from django.urls import path
from . import views

urlpatterns = [
    path("", views.interview_home, name="interview_home"),
    path("<str:session_id>/chat/", views.interview_chat, name="interview_chat"),
]