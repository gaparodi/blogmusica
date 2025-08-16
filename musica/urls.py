from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "musica"

urlpatterns = [
    # Home
    path("", views.inicio, name="inicio"),

    # Listados
    path("notas/<int:pk>/", views.nota_detalle, name="nota_detalle"),
    path("artistas/", views.lista_artistas, name="lista_artistas"),
    path("conciertos/", views.lista_conciertos, name="lista_conciertos"),
    path("lanzamientos/", views.lista_lanzamientos, name="lista_lanzamientos"),
    path("recomendaciones/", views.lista_recomendaciones, name="lista_recomendaciones"),

    # Detalles
    path("artista/<int:pk>/", views.artista_detalle, name="artista_detalle"),
    path("concierto/<int:pk>/", views.concierto_detalle, name="concierto_detalle"),
    path("lanzamiento/<int:pk>/", views.lanzamiento_detalle, name="lanzamiento_detalle"),
    path("recomendacion/<int:pk>/", views.recomendacion_detalle, name="recomendacion_detalle"),

    # Páginas varias
    path("quienes-somos/", views.quienes_somos, name="quienes_somos"),

    # Auth (plantilla en musica/templates/musica/login.html)
    path("login/", auth_views.LoginView.as_view(template_name="musica/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]