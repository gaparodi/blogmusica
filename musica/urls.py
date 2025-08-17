# musica/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'musica'

urlpatterns = [
    # Portada
    path('', views.inicio, name='inicio'),

    # Auth (coinciden con los {% url %} de base.html)
    path('ingresar/', auth_views.LoginView.as_view(template_name='musica/login.html'), name='login'),
    path('salir/', auth_views.LogoutView.as_view(next_page='musica:inicio'), name='logout'),
    path('registrarse/', views.registro, name='register'),

    # Listados (navbar y extras)
    path('artistas/', views.lista_artistas, name='lista_artistas'),
    path('conciertos/', views.lista_conciertos, name='lista_conciertos'),
    path('lanzamientos/', views.lista_lanzamientos, name='lista_lanzamientos'),
    path('recomendaciones/', views.lista_recomendaciones, name='lista_recomendaciones'),
    path('ingresos/', views.ingresos, name='ingresos'),
    path('quienes-somos/', views.quienes_somos, name='quienes_somos'),

    # --- Detalles por PK (tus vistas actuales) ---
    path('nota/<int:pk>/', views.nota_detalle, name='nota_detalle'),
    path('artista/<int:pk>/', views.artista_detalle, name='artista_detalle'),
    path('concierto/<int:pk>/', views.concierto_detalle, name='concierto_detalle'),
    path('lanzamiento/<int:pk>/', views.lanzamiento_detalle, name='lanzamiento_detalle'),
    path('recomendacion/<int:pk>/', views.recomendacion_detalle, name='recomendacion_detalle'),

    # --- Aliases por SLUG (compatibilidad con get_absolute_url/plantillas viejas) ---
    path('nota/<slug:slug>/', views.nota_detalle_slug, name='nota_detail'),
    path('artista/<slug:slug>/', views.artista_detalle_slug, name='artista_detail'),
]