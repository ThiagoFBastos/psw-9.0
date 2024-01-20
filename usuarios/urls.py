from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.logar, name = 'usuarios-login'),
    path('cadastro/', views.cadastro, name = 'usuarios-cadastro'),
    path('logout/', views.logout, name = 'usuarios-logout')
]
