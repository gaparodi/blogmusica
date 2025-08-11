from django.urls import path
from . import views

app_name = 'musica'

urlpatterns = [
    path('', views.inicio, name='inicio'),

    path('artistas/', views.lista_artistas, name='lista_artistas'),
    path('artista/<int:pk>/', views.artista_detalle, name='artista_detalle'),

    path('conciertos/', views.lista_conciertos, name='lista_conciertos'),
    path('concierto/<int:pk>/', views.concierto_detalle, name='concierto_detalle'),

    path('lanzamientos/', views.lista_lanzamientos, name='lista_lanzamientos'),
    path('lanzamiento/<int:pk>/', views.lanzamiento_detalle, name='lanzamiento_detalle'),

    path('recomendaciones/', views.lista_recomendaciones, name='lista_recomendaciones'),
    path('recomendacion/<int:pk>/', views.recomendacion_detalle, name='recomendacion_detalle'),

    path('nota/<int:pk>/', views.nota_detalle, name='nota_detalle'),
]