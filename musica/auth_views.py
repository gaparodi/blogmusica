from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django import forms
from django.template.loader import select_template
from django.http import HttpResponse

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('musica:inicio')

class BootstrapAuthForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Tu usuario",
            "autocomplete": "username",
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Tu contraseña",
            "autocomplete": "current-password",
        })
    )


class BootstrapUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label="Email (opcional)", required=False,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "tu@mail.com"
        })
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Elegí un usuario",
            "autocomplete": "username",
        })
        self.fields["password1"].widget.attrs.update({
            "class": "form-control",
            "autocomplete": "new-password",
        })
        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
            "autocomplete": "new-password",
        })


class LoginViewCustom(LoginView):
    template_name = "musica/login.html"
    authentication_form = BootstrapAuthForm
    redirect_authenticated_user = True


class LogoutViewCustom(LogoutView):
    next_page = "/"


def register_view(request):
    """
    Registro: crea usuario, inicia sesión y redirige a ?next o a inicio.
    Busca automáticamente 'musica/register.html' o 'musica/registrarse.html'.
    """
    if request.method == "POST":
        form = BootstrapUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            next_url = (
                request.POST.get("next")
                or request.GET.get("next")
                or getattr(settings, "LOGIN_REDIRECT_URL", "/")
                or "/"
            )
            return redirect(next_url)
    else:
        form = BootstrapUserCreationForm()

    ctx = {
        "form": form,
        "next": request.GET.get("next", ""),
    }
    # Busca cualquiera de los dos nombres de plantilla
    tmpl = select_template(["musica/register.html", "musica/registrarse.html"])
    return HttpResponse(tmpl.render(ctx, request))