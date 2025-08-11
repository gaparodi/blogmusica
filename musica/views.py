from datetime import datetime, time
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Artista, NotaBlog, Concierto, Lanzamiento, Recomendacion

def inicio(request):
    items = []

    for n in NotaBlog.objects.all():
        items.append({
            'tipo': 'nota',
            'obj': n,
            'orden': timezone.make_naive(n.created_at),
        })

    for c in Concierto.objects.all():
        items.append({
            'tipo': 'concierto',
            'obj': c,
            'orden': timezone.make_naive(c.created_at),
        })

    for l in Lanzamiento.objects.all():
        items.append({
            'tipo': 'lanzamiento',
            'obj': l,
            'orden': timezone.make_naive(l.created_at),
        })

    for r in Recomendacion.objects.all():
        items.append({
            'tipo': 'recomendacion',
            'obj': r,
            'orden': timezone.make_naive(r.created_at),
        })

    items_ultimos = sorted(items, key=lambda x: x['orden'], reverse=True)[:12]
    return render(request, 'musica/inicio.html', {'items': items_ultimos})


def lista_artistas(request):
    artistas = Artista.objects.order_by('nombre')
    return render(request, 'musica/lista_artistas.html', {'artistas': artistas})


def lista_conciertos(request):
    conciertos = Concierto.objects.order_by('-fecha')
    return render(request, 'musica/lista_conciertos.html', {'conciertos': conciertos})


def lista_lanzamientos(request):
    lanzamientos = Lanzamiento.objects.order_by('-fecha_lanzamiento')
    return render(request, 'musica/lista_lanzamientos.html', {'lanzamientos': lanzamientos})


def lista_recomendaciones(request):
    recomendaciones = Recomendacion.objects.order_by('-fecha')
    return render(request, 'musica/lista_recomendaciones.html', {'recomendaciones': recomendaciones})


def nota_detalle(request, pk):
    nota = get_object_or_404(NotaBlog, pk=pk)
    return render(request, 'musica/nota_detalle.html', {'nota': nota})


def artista_detalle(request, pk):
    artista = get_object_or_404(Artista, pk=pk)
    embed_url = None
    if artista.video_youtube:
        embed_url = artista.video_youtube.replace('watch?v=', 'embed/')
    return render(request, 'musica/artista_detalle.html', {
        'artista': artista,
        'embed_url': embed_url,
    })


def concierto_detalle(request, pk):
    concierto = get_object_or_404(Concierto, pk=pk)
    return render(request, 'musica/concierto_detalle.html', {'concierto': concierto})


def lanzamiento_detalle(request, pk):
    lanzamiento = get_object_or_404(Lanzamiento, pk=pk)
    return render(request, 'musica/lanzamiento_detalle.html', {'lanzamiento': lanzamiento})


def recomendacion_detalle(request, pk):
    recomendacion = get_object_or_404(Recomendacion, pk=pk)
    return render(request, 'musica/recomendacion_detalle.html', {'recomendacion': recomendacion})