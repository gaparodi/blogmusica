from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'musica'

urlpatterns = [
    path('', views.inicio, name='inicio'),

    # Login y logout
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='musica:inicio'), name='logout'),

    # Registro
    path('registro/', views.registro, name='registro'),

    # Artistas
    path('artistas/', views.lista_artistas, name='lista_artistas'),
    path('artista/<int:pk>/', views.artista_detalle, name='artista_detalle'),

    # Conciertos
    path('conciertos/', views.lista_conciertos, name='lista_conciertos'),
    path('concierto/<int:pk>/', views.concierto_detalle, name='concierto_detalle'),

    # Lanzamientos
    path('lanzamientos/', views.lista_lanzamientos, name='lista_lanzamientos'),
    path('lanzamiento/<int:pk>/', views.lanzamiento_detalle, name='lanzamiento_detalle'),

    # Recomendaciones
    path('recomendaciones/', views.lista_recomendaciones, name='lista_recomendaciones'),
    path('recomendacion/<int:pk>/', views.recomendacion_detalle, name='recomendacion_detalle'),

    # Notas
    path('nota/<int:pk>/', views.nota_detalle, name='nota_detalle'),

    # Quiénes Somos
    path('quienes-somos/', views.quienes_somos, name='quienes_somos'),
]
