"""
Django settings for blogmusica project.
"""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Seguridad
SECRET_KEY = os.environ.get(
    "DJ_SECRET_KEY",
    "django-insecure-f3+8eh3wlanx3(w7v3(d6&k-sy!7*=gscsk#ribol8c*hc7o(o"  # <-- solo para desarrollo
)

# Debug por variable de entorno (True por defecto en local)
DEBUG = os.environ.get("DJ_DEBUG", "True") == "True"

# Hosts permitidos: local + (opcional) dominio en PA
_allowed_env = os.environ.get("DJ_ALLOWED_HOST", "")
ALLOWED_HOSTS = ["127.0.0.1", "localhost"] + ([_allowed_env] if _allowed_env else [])
# Si prefieres hardcodear, añade por ejemplo: "TU_USUARIO.pythonanywhere.com"

# Apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "musica",
]

# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "blogmusica.urls"

# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Si tienes una carpeta de proyecto "templates", se usa; si no, no pasa nada.
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,  # Buscará también dentro de musica/templates/
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "blogmusica.wsgi.application"

# Base de datos (sqlite por ahora)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validators
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# i18n
LANGUAGE_CODE = "es"   # español por defecto
TIME_ZONE = "UTC"      # cambia si quieres, ej: "America/Argentina/Buenos_Aires"
USE_I18N = True
USE_TZ = True

# Static & media
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"   # para collectstatic en producción

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"