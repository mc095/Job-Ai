from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='portfolio_home'),
    path('create/', views.create_portfolio, name='create_portfolio'),
    path('select-template/', views.select_template, name='select_template'),
    path('dashboard/', views.portfolio_dashboard, name='portfolio_dashboard'),
    path('download/', views.download_portfolio, name='download_portfolio'),
    path('new/', views.new_portfolio, name='new_portfolio'),
]

