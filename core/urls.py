# core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Página inicial com busca
    path('', views.home, name='home'),
    
    # Cadastros
    path('cadastrar-cidade/', views.cadastrar_cidade, name='cadastrar_cidade'),
    path('cadastrar-media/', views.cadastrar_media, name='cadastrar_media'),
    path('deletar_media/<int:fotografia_pk>/', views.deletar_media_confirm, name='core_deletar_media_confirm'),

    
    # Listagem e detalhes
    path('cidades/', views.listar_cidades, name='listar_cidades'),
    path('cidade/', views.listar_medias_cidade, name='listar_medias_cidade'),
    path('media/<int:media_id>/', views.detalhe_media, name='detalhe_media'),
    # APIs
   # path('api/cidades/autocomplete/', views.api_cidades_autocomplete, name='api_autocomplete'),
   # path('api/estatisticas/', views.estatisticas, name='api_estatisticas'),
]
