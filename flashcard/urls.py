from django.urls import path
from . import views

urlpatterns = [
    path('novo_flashcard/', views.novo_flashcard, name = 'flashcard-novo_flashcard'),
    path('deletar_flashcard/<int:id>/', views.deletar_flashcard, name = 'flashcard-deletar_flashcard'),
    path('iniciar_desafio/', views.iniciar_desafio, name = 'flashcard-iniciar_desafio'),
    path('listar_desafio/', views.listar_desafio, name = 'flashcard-listar_desafio'),
    path('desafio/<int:id>/', views.desafio, name = 'flashcard-desafio'),
    path('responder_flashcard/<int:id>/', views.respondeer_flashcard, name = 'responder_flashcard'),
    path('relatorio/<int:id>/', views.relatorio, name = 'relatorio'),
]
