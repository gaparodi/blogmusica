from django.contrib import admin
from .models import (
    Artista,
    NotaBlog,
    Concierto,
    Lanzamiento,
    Recomendacion,
    Comentario,
)


@admin.register(NotaBlog)
class NotaBlogAdmin(admin.ModelAdmin):
    list_display = ("titulo", "slug", "created_at")
    list_filter = ("created_at",)
    search_fields = ("titulo", "contenido", "slug")
    prepopulated_fields = {"slug": ("titulo",)}
    ordering = ("-created_at",)


@admin.register(Artista)
class ArtistaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "pais", "genero_principal", "created_at")
    list_filter = ("pais", "genero_principal")
    search_fields = ("nombre", "pais", "genero_principal")
    ordering = ("nombre",)


@admin.register(Concierto)
class ConciertoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "ubicacion", "fecha", "created_at")
    list_filter = ("fecha", "ubicacion")
    search_fields = ("nombre", "ubicacion")
    ordering = ("-fecha",)


@admin.register(Lanzamiento)
class LanzamientoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "artista", "fecha_lanzamiento", "created_at")
    list_filter = ("fecha_lanzamiento", "artista")
    search_fields = ("titulo", "artista__nombre")
    ordering = ("-fecha_lanzamiento",)


@admin.register(Recomendacion)
class RecomendacionAdmin(admin.ModelAdmin):
    list_display = ("titulo", "artista", "fecha", "created_at")
    list_filter = ("fecha", "artista")
    search_fields = ("titulo", "artista__nombre")
    ordering = ("-fecha",)


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ("nota", "autor", "created_at")
    list_filter = ("created_at",)
    search_fields = ("nota__titulo", "autor__username", "contenido")
    ordering = ("-created_at",)