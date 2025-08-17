from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required

from .models import NotaBlog, Comentario


class NotaDetailView(DetailView):
    model = NotaBlog
    template_name = 'musica/nota_detail.html'
    context_object_name = 'nota'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        # Optimiza: trae solo campos necesarios y prefetch de comentarios+autor
        return (super().get_queryset()
                .only('id', 'titulo', 'slug', 'contenido', 'imagen_destacada', 'created_at')
                .prefetch_related('comentarios__autor'))


@login_required
def agregar_comentario(request, slug):
    nota = get_object_or_404(NotaBlog, slug=slug)
    if request.method == 'POST':
        contenido = (request.POST.get('contenido') or '').strip()
        if contenido:
            Comentario.objects.create(nota=nota, autor=request.user, contenido=contenido)
    return redirect(nota.get_absolute_url() + '#comentarios')