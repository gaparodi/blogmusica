from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils.text import Truncator
from django.db import models
from django.urls import reverse  # necesario para _detail_url

from .models import Artista, NotaBlog, Concierto, Lanzamiento, Recomendacion
from .forms import ComentarioForm


# ----------------------------
# Helpers
# ----------------------------

def _get_created(obj):
    """
    Devuelve la 'fecha de carga' que usa la portada.
    Soporta created_at / creado_at; si no existen, usa now() para no romper.
    """
    return (
        getattr(obj, 'created_at', None)
        or getattr(obj, 'creado_at', None)
        or timezone.now()
    )

def _first_imagefield_url(obj):
    """
    Busca de forma GENÉRICA el primer ImageField/FileField con imagen en el modelo,
    sin importar el nombre del campo. Evita depender de 'imagen', 'foto', etc.
    """
    try:
        for f in obj._meta.get_fields():
            # Solo campos concretos (no relaciones)
            if isinstance(f, (models.ImageField, models.FileField)):
                name = f.name
                fileobj = getattr(obj, name, None)
                if fileobj:
                    try:
                        url = fileobj.url
                        if url:
                            return url
                    except Exception:
                        continue
    except Exception:
        pass
    return None

def _image_url_for(obj):
    """
    Elige una imagen para portada/detalle:
    1) Intenta nombres comunes.
    2) Si no, escanea cualquier Image/FileField.
    3) Fallback: imagen del artista vinculado.
    """
    # 1) Campos comunes
    for fname in ('imagen', 'image', 'portada', 'cover', 'foto', 'thumb', 'imagen_principal', 'imagen_nota'):
        f = getattr(obj, fname, None)
        if f:
            try:
                return f.url
            except Exception:
                pass

    # 2) Escaneo genérico
    url = _first_imagefield_url(obj)
    if url:
        return url

    # 3) Fallback: imagen del artista
    artista = getattr(obj, 'artista', None)
    if artista:
        aurl = _first_imagefield_url(artista)
        if aurl:
            return aurl
        for fname in ('imagen', 'image', 'foto', 'avatar'):
            f = getattr(artista, fname, None)
            if f:
                try:
                    return f.url
                except Exception:
                    pass

    return None

def _text_first(obj, *fieldnames):
    """Primer campo de texto no vacío que exista en el objeto."""
    for fname in fieldnames:
        val = getattr(obj, fname, None)
        if val:
            return str(val)
    return ""

def _build_preview(tipo, obj):
    """
    Texto corto para la tarjeta de portada.
    - notas: contenido/descripcion/texto/resumen
    - conciertos: descripcion o 'Fecha • Lugar'
    - lanzamientos: descripcion
    - recomendaciones: descripcion
    """
    if tipo == 'nota':
        text = _text_first(obj, 'contenido', 'descripcion', 'texto', 'resumen')
    elif tipo == 'concierto':
        text = _text_first(obj, 'descripcion', 'detalle', 'texto')
        if not text:
            parts = []
            fecha = getattr(obj, 'fecha', None)
            if fecha:
                try:
                    parts.append(f"Fecha: {fecha.strftime('%d/%m/%Y')}")
                except Exception:
                    parts.append(f"Fecha: {fecha}")
            lugar = getattr(obj, 'lugar', None)
            if lugar:
                parts.append(f"Lugar: {lugar}")
            text = " • ".join(parts)
    elif tipo == 'lanzamiento':
        text = _text_first(obj, 'descripcion', 'detalle', 'texto')
    elif tipo == 'recomendacion':
        text = _text_first(obj, 'descripcion', 'detalle', 'texto', 'resumen')
    else:
        text = ""
    return Truncator(text).chars(160)

def _detail_url(tipo, obj):
    """
    Devuelve la URL al detalle del item.
    - Si el objeto define get_absolute_url(), se usa.
    - Si no, armamos la URL por PK usando los names definidos en urls.py.
    """
    # 1) Si el modelo tiene get_absolute_url usable
    try:
        if hasattr(obj, 'get_absolute_url'):
            url = obj.get_absolute_url()
            if url:
                return url
    except Exception:
        pass

    # 2) Por tipo -> name por PK
    try:
        if tipo == 'nota':
            return reverse('musica:nota_detalle', kwargs={'pk': obj.pk})
        if tipo == 'concierto':
            return reverse('musica:concierto_detalle', kwargs={'pk': obj.pk})
        if tipo == 'lanzamiento':
            return reverse('musica:lanzamiento_detalle', kwargs={'pk': obj.pk})
        if tipo == 'recomendacion':
            return reverse('musica:recomendacion_detalle', kwargs={'pk': obj.pk})
        if tipo == 'artista':
            return reverse('musica:artista_detalle', kwargs={'pk': obj.pk})
    except Exception:
        pass

    # 3) Fallback
    return '#'

def _item(tipo, obj, titulo, url=None):
    return {
        'tipo': tipo,
        'obj': obj,
        'orden': timezone.make_naive(_get_created(obj)),
        'titulo': titulo,
        'image_url': _image_url_for(obj),
        'preview': _build_preview(tipo, obj),
        'url': url or _detail_url(tipo, obj),  # href de cada card
    }

def _safe_search(qs, query, fields_or_relations):
    """
    Intenta filtrar por múltiples campos sin romper si alguno no existe.
    Soporta relaciones (p.ej. 'artista__nombre').
    """
    q = Q()
    for name in fields_or_relations:
        try:
            first_hop = name.split('__', 1)[0]
            qs.model._meta.get_field(first_hop)
            q |= Q(**{f"{name}__icontains": query})
        except Exception:
            continue
    if not q:
        # Fallback: título si existe; si no, no filtra nada.
        try:
            qs.model._meta.get_field('titulo')
            q = Q(titulo__icontains=query)
        except Exception:
            q = Q()
    return qs.filter(q) if q else qs.none()


# ----------------------------
# Autenticación
# ----------------------------

def login_view(request):
    if request.user.is_authenticated:
        return redirect('musica:inicio')
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        auth_login(request, form.get_user())
        return redirect('musica:inicio')
    return render(request, 'musica/login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('musica:inicio')

def registro(request):
    if request.user.is_authenticated:
        return redirect('musica:inicio')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('musica:inicio')
    else:
        form = UserCreationForm()
    return render(request, 'musica/registro.html', {'form': form})


# ----------------------------
# Listados y detalle
# ----------------------------

def lista_artistas(request):
    artistas = Artista.objects.order_by('nombre')
    return render(request, 'musica/lista_artistas.html', {'artistas': artistas})

def artista_detalle(request, pk):
    artista = get_object_or_404(Artista, pk=pk)
    embed_url = None
    if getattr(artista, 'video_youtube', None):
        embed_url = artista.video_youtube.replace('watch?v=', 'embed/')
    return render(request, 'musica/artista_detalle.html', {'artista': artista, 'embed_url': embed_url})

def lista_conciertos(request):
    conciertos = Concierto.objects.order_by('-fecha')
    return render(request, 'musica/lista_conciertos.html', {'conciertos': conciertos})

def concierto_detalle(request, pk):
    concierto = get_object_or_404(Concierto, pk=pk)
    return render(request, 'musica/concierto_detalle.html', {'concierto': concierto})

def lista_lanzamientos(request):
    # Orden por fecha del evento
    lanzamientos = Lanzamiento.objects.order_by('-fecha_lanzamiento')
    return render(request, 'musica/lista_lanzamientos.html', {'lanzamientos': lanzamientos})

def lanzamiento_detalle(request, pk):
    lanzamiento = get_object_or_404(Lanzamiento, pk=pk)
    return render(request, 'musica/lanzamiento_detalle.html', {'lanzamiento': lanzamiento})

def lista_recomendaciones(request):
    recomendaciones = Recomendacion.objects.order_by('-id')
    return render(request, 'musica/lista_recomendaciones.html', {'recomendaciones': recomendaciones})

def recomendacion_detalle(request, pk):
    recomendacion = get_object_or_404(Recomendacion, pk=pk)
    return render(request, 'musica/recomendacion_detalle.html', {'recomendacion': recomendacion})

def nota_detalle(request, pk):
    nota = get_object_or_404(NotaBlog, pk=pk)

    # <<< MODIFICACIÓN: calcular URL de imagen robusta y pasarla al template >>>
    image_url = _image_url_for(nota)

    comentarios = getattr(nota, 'comentarios', None)
    if comentarios is not None and hasattr(comentarios, 'order_by'):
        comentarios = comentarios.order_by('-created_at')
    else:
        comentarios = []

    if request.user.is_authenticated and request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.nota = nota
            comentario.autor = request.user
            comentario.save()
            return redirect('musica:nota_detalle', pk=nota.pk)
    else:
        form = ComentarioForm() if request.user.is_authenticated else None

    return render(request, 'musica/nota_detalle.html', {
        'nota': nota,
        'image_url': image_url,   # << clave para mostrar la imagen en la nota
        'comentarios': comentarios,
        'form': form
    })

def quienes_somos(request):
    return render(request, 'musica/quienes_somos.html')


# ----------------------------
# Wrappers por SLUG (compatibilidad)
# ----------------------------

def nota_detalle_slug(request, slug):
    nota = get_object_or_404(NotaBlog, slug=slug)
    return nota_detalle(request, pk=nota.pk)

def artista_detalle_slug(request, slug):
    artista = get_object_or_404(Artista, slug=slug)
    return artista_detalle(request, pk=artista.pk)


# ----------------------------
# Ingresos (cronológico por carga)
# ----------------------------

def ingresos(request):
    """
    Lista plana de todo lo cargado (orden cronológico de carga).
    """
    items = []

    for n in NotaBlog.objects.all():
        items.append(_item('nota', n, getattr(n, 'titulo', 'Nota')))

    for c in Concierto.objects.all():
        items.append(_item('concierto', c, getattr(c, 'nombre', None) or getattr(c, 'titulo', 'Concierto')))

    for l in Lanzamiento.objects.all():
        items.append(_item('lanzamiento', l, getattr(l, 'titulo', 'Lanzamiento')))

    for r in Recomendacion.objects.all():
        items.append(_item('recomendacion', r, getattr(r, 'titulo', 'Recomendación')))

    items_ordenados = sorted(items, key=lambda x: x['orden'], reverse=True)
    return render(request, 'musica/ingresos.html', {'items': items_ordenados})


# ----------------------------
# Portada con buscador (orden por fecha de carga)
# ----------------------------

def inicio(request):
    query = request.GET.get('q', '').strip()
    items = []

    # NOTAS
    notas_qs = NotaBlog.objects.all()
    if query:
        notas_qs = _safe_search(notas_qs, query, ['titulo', 'contenido', 'descripcion', 'texto', 'resumen', 'artista__nombre'])
    for n in notas_qs:
        items.append(_item('nota', n, getattr(n, 'titulo', 'Nota')))

    # CONCIERTOS (en portada, por fecha de carga igual que los demás tipos)
    conciertos_qs = Concierto.objects.all()
    if query:
        conciertos_qs = _safe_search(conciertos_qs, query, ['nombre', 'titulo', 'descripcion', 'lugar', 'artista__nombre'])
    for c in conciertos_qs:
        titulo = getattr(c, 'nombre', None) or getattr(c, 'titulo', 'Concierto')
        items.append(_item('concierto', c, titulo))

    # LANZAMIENTOS
    lanzamientos_qs = Lanzamiento.objects.all()
    if query:
        lanzamientos_qs = _safe_search(lanzamientos_qs, query, ['titulo', 'descripcion', 'artista__nombre'])
    for l in lanzamientos_qs:
        items.append(_item('lanzamiento', l, getattr(l, 'titulo', 'Lanzamiento')))

    # RECOMENDACIONES
    recomendaciones_qs = Recomendacion.objects.all()
    if query:
        recomendaciones_qs = _safe_search(recomendaciones_qs, query, ['titulo', 'descripcion', 'texto', 'resumen', 'artista__nombre'])
    for r in recomendaciones_qs:
        items.append(_item('recomendacion', r, getattr(r, 'titulo', 'Recomendación')))

    # Ordenar por fecha de carga (no por fecha de evento)
    items_ultimos = sorted(items, key=lambda x: x['orden'], reverse=True)[:12]

    # Últimas notas (pie). Usamos -id (si no hay created_at) para simple “reciente”.
    ultimas_notas = NotaBlog.objects.order_by('-id')[:6]

    return render(request, 'musica/inicio.html', {
        'items': items_ultimos,
        'ultimas_notas': ultimas_notas,
        'query': query,
    })