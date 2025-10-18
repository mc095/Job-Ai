from django.urls import path
from . import views
urlpatterns = [
    path("", views.home, name="exam_home"),
    path("loading/", views.exam_loading, name="exam_loading"),
    path("import/", views.import_exam, name="exam_import"),
    path("<str:exam_id>/<int:question_num>/", views.exam_test, name="exam_test"),
    path("result/", views.exam_result, name="exam_result"),
]
