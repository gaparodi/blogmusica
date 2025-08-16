from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify


class Artista(models.Model):
    nombre = models.CharField(max_length=200)
    pais = models.CharField(max_length=100, blank=True)
    genero_principal = models.CharField(max_length=100, blank=True)
    biografia = models.TextField(blank=True)
    sitio_web = models.URLField(blank=True)
    imagen = models.ImageField(upload_to='artistas/', blank=True, null=True)
    video_youtube = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self) -> str:
        return self.nombre


class NotaBlog(models.Model):
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    contenido = models.TextField()
    imagen_destacada = models.ImageField(upload_to='notas/', blank=True, null=True)
    tags = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            base = slugify(self.titulo) or "nota"
            s = base
            n = 1
            while NotaBlog.objects.filter(slug=s).exists():
                n += 1
                s = f"{base}-{n}"
            self.slug = s
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse('musica:nota_detail', kwargs={'slug': self.slug})

    def __str__(self) -> str:
        return self.titulo


class Concierto(models.Model):
    nombre = models.CharField(max_length=255)
    detalle = models.TextField(blank=True)
    ubicacion = models.CharField(max_length=255, blank=True)
    fecha = models.DateTimeField()
    imagen = models.ImageField(upload_to='conciertos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self) -> str:
        return self.nombre


class Lanzamiento(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    artista = models.ForeignKey(Artista, on_delete=models.CASCADE, related_name='lanzamientos')
    fecha_lanzamiento = models.DateField()
    imagen = models.ImageField(upload_to='lanzamientos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_lanzamiento']

    def __str__(self) -> str:
        return f"{self.titulo} - {self.artista.nombre}"


class Recomendacion(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    artista = models.ForeignKey(Artista, on_delete=models.CASCADE, related_name='recomendaciones')
    fecha = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self) -> str:
        return self.titulo


class Comentario(models.Model):
    nota = models.ForeignKey('NotaBlog', on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contenido = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.autor} - {self.nota.titulo[:20]}"