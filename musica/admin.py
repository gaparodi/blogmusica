from django.contrib import admin
from django.utils.html import format_html
from .models import Artista, NotaBlog, Concierto, Lanzamiento, Recomendacion

@admin.register(Artista)
class ArtistaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'pais', 'genero_principal']
    readonly_fields = ['vista_previa_imagen']
    fields = [
        'nombre', 'pais', 'genero_principal',
        'biografia', 'sitio_web', 'imagen',
        'video_youtube', 'vista_previa_imagen'
    ]

    def vista_previa_imagen(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="max-height:200px;" />', obj.imagen.url)
        return "(Sin imagen)"
    vista_previa_imagen.short_description = "Vista previa"


@admin.register(NotaBlog)
class NotaBlogAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'created_at', 'miniatura')
    search_fields = ('titulo', 'contenido', 'tags')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    fields = ('titulo', 'contenido', 'imagen_destacada', 'tags', 'created_at')

    def miniatura(self, obj):
        if obj.imagen_destacada:
            return format_html('<img src="{}" style="max-height:50px;" />', obj.imagen_destacada.url)
        return "(Sin imagen)"
    miniatura.short_description = "Miniatura"


@admin.register(Concierto)
class ConciertoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha', 'ubicacion')
    fields = ('nombre', 'detalle', 'ubicacion', 'fecha', 'imagen')


@admin.register(Lanzamiento)
class LanzamientoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'artista', 'fecha_lanzamiento')
    search_fields = ('titulo', 'artista__nombre')
    list_filter = ('fecha_lanzamiento',)
    fields = ('titulo', 'artista', 'fecha_lanzamiento', 'descripcion', 'imagen')


@admin.register(Recomendacion)
class RecomendacionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'artista', 'fecha')
    search_fields = ('titulo', 'artista__nombre')
    list_filter = ('fecha',)
    fields = ('titulo', 'artista', 'fecha', 'descripcion')