from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_treinamentos, name='listar_treinamentos'),
    path('cadastrar/', views.cadastrar_treinamento, name='cadastrar_treinamento'),
    path('editar/<int:pk>/', views.editar_treinamento, name='editar_treinamento'),
    path('excluir/<int:pk>/', views.excluir_treinamento, name='excluir_treinamento'),
    path('atribuir/', views.atribuir_treinamento, name='atribuir_treinamento'),
    path('colaboradores/<int:pk>/', views.listar_colaboradores_treinamento, name='listar_colaboradores_treinamento'),
    path('concluir/<int:pk>/', views.registrar_conclusao, name='registrar_conclusao'),
    path('remover/<int:pk>/', views.remover_colaborador_treinamento, name='remover_colaborador_treinamento'),
    path('ajax/carregar-colaboradores/', views.carregar_colaboradores, name='ajax_carregar_colaboradores'),
]