from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login as auth_login
from .models import Artista, NotaBlog, Concierto, Lanzamiento, Recomendacion
from .forms import ComentarioForm
from django.contrib.auth.decorators import login_required

# --- LOGIN ---
def login_view(request):
    if request.user.is_authenticated:
        return redirect('musica:inicio')

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        auth_login(request, form.get_user())
        return redirect('musica:inicio')

    return render(request, 'musica/login.html', {'form': form})

# --- REGISTRO ---
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

# --- PORTADA ---
def inicio(request):
    items = []

    # Cargar todos los elementos
    for n in NotaBlog.objects.all():
        items.append({'tipo': 'nota', 'obj': n, 'orden': timezone.make_naive(n.created_at)})
    for c in Concierto.objects.all():
        items.append({'tipo': 'concierto', 'obj': c, 'orden': timezone.make_naive(c.created_at)})
    for l in Lanzamiento.objects.all():
        items.append({'tipo': 'lanzamiento', 'obj': l, 'orden': timezone.make_naive(l.created_at)})
    for r in Recomendacion.objects.all():
        items.append({'tipo': 'recomendacion', 'obj': r, 'orden': timezone.make_naive(r.created_at)})

    items_ultimos = sorted(items, key=lambda x: x['orden'], reverse=True)[:12]

    return render(request, 'musica/inicio.html', {'items': items_ultimos})

# --- ARTISTAS ---
def lista_artistas(request):
    artistas = Artista.objects.order_by('nombre')
    return render(request, 'musica/lista_artistas.html', {'artistas': artistas})

def artista_detalle(request, pk):
    artista = get_object_or_404(Artista, pk=pk)
    embed_url = None
    if artista.video_youtube:
        embed_url = artista.video_youtube.replace('watch?v=', 'embed/')
    return render(request, 'musica/artista_detalle.html', {'artista': artista, 'embed_url': embed_url})

# --- CONCIERTOS ---
def lista_conciertos(request):
    conciertos = Concierto.objects.order_by('-fecha')
    return render(request, 'musica/lista_conciertos.html', {'conciertos': conciertos})

def concierto_detalle(request, pk):
    concierto = get_object_or_404(Concierto, pk=pk)
    return render(request, 'musica/concierto_detalle.html', {'concierto': concierto})

# --- LANZAMIENTOS ---
def lista_lanzamientos(request):
    lanzamientos = Lanzamiento.objects.order_by('-fecha_lanzamiento')
    return render(request, 'musica/lista_lanzamientos.html', {'lanzamientos': lanzamientos})

def lanzamiento_detalle(request, pk):
    lanzamiento = get_object_or_404(Lanzamiento, pk=pk)
    return render(request, 'musica/lanzamiento_detalle.html', {'lanzamiento': lanzamiento})

# --- RECOMENDACIONES ---
def lista_recomendaciones(request):
    recomendaciones = Recomendacion.objects.order_by('-fecha')
    return render(request, 'musica/lista_recomendaciones.html', {'recomendaciones': recomendaciones})

def recomendacion_detalle(request, pk):
    recomendacion = get_object_or_404(Recomendacion, pk=pk)
    return render(request, 'musica/recomendacion_detalle.html', {'recomendacion': recomendacion})

# --- NOTAS ---
def nota_detalle(request, pk):
    nota = get_object_or_404(NotaBlog, pk=pk)
    comentarios = nota.comentarios.order_by('-created_at')
    form = None

    if request.user.is_authenticated:
        if request.method == 'POST':
            form = ComentarioForm(request.POST)
            if form.is_valid():
                comentario = form.save(commit=False)
                comentario.nota = nota
                comentario.autor = request.user
                comentario.save()
                return redirect('musica:nota_detalle', pk=nota.pk)
        else:
            form = ComentarioForm()

    return render(request, 'musica/nota_detalle.html', {
        'nota': nota,
        'comentarios': comentarios,
        'form': form
    })

# --- QUIÉNES SOMOS ---
def quienes_somos(request):
    return render(request, 'musica/quienes_somos.html')


# --- PORTADA CON BUSCADOR ---
def inicio(request):
    query = request.GET.get('q', '')  # Obtener término de búsqueda
    items = []

    # Filtrar por búsqueda si existe
    if query:
        notas = NotaBlog.objects.filter(titulo__icontains=query)
        conciertos = Concierto.objects.filter(nombre__icontains=query)
        lanzamientos = Lanzamiento.objects.filter(titulo__icontains=query)
        recomendaciones = Recomendacion.objects.filter(titulo__icontains=query)
    else:
        notas = NotaBlog.objects.all()
        conciertos = Concierto.objects.all()
        lanzamientos = Lanzamiento.objects.all()
        recomendaciones = Recomendacion.objects.all()

    # Unir todos los elementos en la lista items
    for n in notas:
        items.append({'tipo': 'nota', 'obj': n, 'orden': timezone.make_naive(n.created_at)})
    for c in conciertos:
        items.append({'tipo': 'concierto', 'obj': c, 'orden': timezone.make_naive(c.created_at)})
    for l in lanzamientos:
        items.append({'tipo': 'lanzamiento', 'obj': l, 'orden': timezone.make_naive(l.created_at)})
    for r in recomendaciones:
        items.append({'tipo': 'recomendacion', 'obj': r, 'orden': timezone.make_naive(r.created_at)})

    # Ordenar por fecha descendente y limitar a 12 últimos
    items_ultimos = sorted(items, key=lambda x: x['orden'], reverse=True)[:12]

    return render(request, 'musica/inicio.html', {
        'items': items_ultimos,
        'query': query  # pasar término al template para mantener el valor en el input
    })
