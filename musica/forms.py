# musica/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Comentario  # Asegúrate que este modelo exista

# --- FORMULARIO DE REGISTRO PERSONALIZADO ---
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Quitar todos los help_text
        for field in self.fields.values():
            field.help_text = ""

        # Agregar clases de Bootstrap a los inputs
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing + " form-control").strip()

# --- FORMULARIO DE COMENTARIOS ---
class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['contenido']  # Cambia 'contenido' por el nombre real del campo de tu modelo
        widgets = {
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
