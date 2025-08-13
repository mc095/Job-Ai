from django.urls import path
from . import views
urlpatterns = [
    path("", views.home, name="exam_home"),
    path("loading/", views.exam_loading, name="exam_loading"),
    path("<str:exam_id>/", views.exam_test, name="exam_test"),
    path("<str:exam_id>/result/", views.exam_result, name="exam_result"),
]
