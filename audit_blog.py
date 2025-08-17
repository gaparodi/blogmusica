import os
import re
import sys
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import get_resolver, URLPattern, URLResolver


URL_TAG_RE = re.compile(r"""{%\s*url\s+['"]([^'"]+)['"]""")
REVERSE_RE = re.compile(r"""reverse(?:_lazy)?\(\s*['"]([^'"]+)['"]""")

class Command(BaseCommand):
    help = "Audita URLs, templates y settings para detectar inconsistencias típicas (NoReverseMatch, templates faltantes, etc.)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--project-root",
            default=str(Path(settings.BASE_DIR)),
            help="Ruta raíz del proyecto (por defecto settings.BASE_DIR)",
        )
        parser.add_argument(
            "--templates-dir",
            default=None,
            help="Carpeta de templates adicional a escanear (por defecto TEMPLATES['DIRS'])",
        )
        parser.add_argument(
            "--apps",
            nargs="*",
            default=None,
            help="Lista de apps a escanear (.py y templates en sus directorios). Por defecto todas en INSTALLED_APPS propias.",
        )

    def handle(self, *args, **opts):
        base_dir = Path(opts["project_root"]).resolve()

        self.stdout.write(self.style.NOTICE("=== AUDITORÍA DEL BLOG ==="))
        self.stdout.write(f"BASE_DIR: {base_dir}")

        # 1) Resolver de URLs: recolectar todos los names disponibles
        self.stdout.write(self.style.NOTICE("\n[1] Relevando NAMES de URL registrados..."))
        all_url_names = set()
        patterns_info = []
        self._collect_urlpatterns(get_resolver(), all_url_names, patterns_info)

        if not all_url_names:
            self.stdout.write(self.style.ERROR("No se registraron URL names."))
        else:
            self.stdout.write(f"Total de URL names registrados: {len(all_url_names)}")
            # Mostrar algunos clave si existen
            for key in ("login", "logout", "musica:inicio", "inicio"):
                if key in all_url_names:
                    self.stdout.write(self.style.SUCCESS(f"✔ name registrado: {key}"))
                else:
                    self.stdout.write(self.style.WARNING(f"• name NO encontrado: {key}"))

        # 2) Escanear templates: buscar {% url '...' %}
        self.stdout.write(self.style.NOTICE("\n[2] Escaneando templates para detectar {% url 'name' %} inexistentes..."))
        template_dirs = set()

        # Agregar DIRS desde settings.TEMPLATES
        for conf in settings.TEMPLATES:
            for d in conf.get("DIRS", []):
                template_dirs.add(Path(d).resolve())

        if opts["templates_dir"]:
            template_dirs.add(Path(opts["templates_dir"]).resolve())

        # Agregar templates dentro de apps (APP_DIRS=True)
        # Buscar carpetas "<app>/templates"
        app_dirs = self._infer_local_apps()
        for app_path in app_dirs:
            tdir = app_path / "templates"
            if tdir.exists():
                template_dirs.add(tdir.resolve())

        missing_from_templates = []
        scanned_templates = 0

        for tdir in sorted(template_dirs):
            for root, _dirs, files in os.walk(tdir):
                for f in files:
                    if f.endswith(".html"):
                        scanned_templates += 1
                        path = Path(root) / f
                        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                            content = fh.read()
                        for m in URL_TAG_RE.finditer(content):
                            name = m.group(1)
                            if name not in all_url_names:
                                missing_from_templates.append((str(path), name))

        self.stdout.write(f"Templates escaneados: {scanned_templates}")
        if missing_from_templates:
            self.stdout.write(self.style.ERROR("Referencias a URL names inexistentes en templates:"))
            for path, name in missing_from_templates:
                self.stdout.write(f"  - {path}: {% url '{name}' %}  -> NO registrado")
        else:
            self.stdout.write(self.style.SUCCESS("✔ No se detectaron {% url %} con names inexistentes."))

        # 3) Escanear código Python: reverse('name')
        self.stdout.write(self.style.NOTICE("\n[3] Escaneando código Python para reverse('name') inexistentes..."))

        py_dirs = set()
        py_dirs.add(base_dir)
        for app_path in app_dirs:
            py_dirs.add(app_path.resolve())

        missing_from_py = []
        scanned_py = 0
        for d in sorted(py_dirs):
            for root, _dirs, files in os.walk(d):
                # Excluir venv, migrations compiladas, etc.
                if any(ig in root for ig in (".venv", "venv", "env", "node_modules", "__pycache__")):
                    continue
                for f in files:
                    if f.endswith(".py"):
                        scanned_py += 1
                        path = Path(root) / f
                        try:
                            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                                content = fh.read()
                        except Exception:
                            continue
                        for m in REVERSE_RE.finditer(content):
                            name = m.group(1)
                            if name not in all_url_names:
                                missing_from_py.append((str(path), name))

        self.stdout.write(f"Archivos .py escaneados: {scanned_py}")
        if missing_from_py:
            self.stdout.write(self.style.ERROR("Referencias a reverse('name') inexistentes en Python:"))
            for path, name in missing_from_py:
                self.stdout.write(f"  - {path}: reverse('{name}')  -> NO registrado")
        else:
            self.stdout.write(self.style.SUCCESS("✔ No se detectaron reverse('...') con names inexistentes."))

        # 4) Chequeos de settings
        self.stdout.write(self.style.NOTICE("\n[4] Chequeos de settings (coherencia mínima) ..."))
        self._check_settings()

        # 5) Recomendaciones rápidas
        self.stdout.write(self.style.NOTICE("\n[5] Recomendaciones / Próximos pasos"))
        if "logout" not in all_url_names:
            self.stdout.write("- Falta registrar una ruta con name='logout'. Ejemplo:")
            self.stdout.write("    path('salir/', django.contrib.auth.views.LogoutView.as_view(), name='logout')")
        if "login" not in all_url_names and getattr(settings, "LOGIN_URL", None):
            self.stdout.write(f"- LOGIN_URL está en {settings.LOGIN_URL}, pero no hay name='login'. Definí:")
            self.stdout.write("    path('ingresar/', django.contrib.auth.views.LoginView.as_view(), name='login')")
            self.stdout.write("  y crea templates/registration/login.html si usás LoginView.")
        if missing_from_templates or missing_from_py:
            self.stdout.write("- Corregí los names detectados arriba. Si el name es correcto, verificá namespaces (ej. 'accounts:logout').")

        self.stdout.write(self.style.SUCCESS("\n✔ Auditoría finalizada."))

    # --- helpers ---

    def _collect_urlpatterns(self, resolver, name_set, patterns_info, prefix=""):
        """
        Recorre el árbol de URLConf y junta todos los names.
        """
        for p in resolver.url_patterns:
            if isinstance(p, URLPattern):
                if p.name:
                    name_set.add(p.name if not prefix else f"{prefix}{p.name}")
                    patterns_info.append((p.name, str(p.pattern)))
            elif isinstance(p, URLResolver):
                ns = p.namespace
                new_prefix = prefix
                if ns:
                    # si hay namespace, los names reales son namespace:name
                    new_prefix = f"{ns}:"
                self._collect_urlpatterns(p, name_set, patterns_info, prefix=new_prefix)

    def _infer_local_apps(self):
        """
        Devuelve rutas Path de apps 'propias' (las que están en INSTALLED_APPS y existen como carpeta dentro del BASE_DIR).
        """
        app_paths = []
        base_dir = Path(settings.BASE_DIR)
        for app in settings.INSTALLED_APPS:
            # filtrar solo las apps que parecen locales (carpeta dentro del proyecto)
            candidate = base_dir / app.split(".")[0]
            if candidate.exists() and candidate.is_dir():
                app_paths.append(candidate)
        return app_paths

    def _check_settings(self):
        ok = True

        # TEMPLATES context processors
        cps = []
        for conf in settings.TEMPLATES:
            cps.extend(conf.get("OPTIONS", {}).get("context_processors", []))
        required = {
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        }
        missing = required - set(cps)
        if missing:
            ok = False
            self.stdout.write(self.style.ERROR(f"- Faltan context processors: {missing}"))
        else:
            self.stdout.write(self.style.SUCCESS("✔ Context processors mínimos OK."))

        # INSTALLED_APPS
        for must in ("django.contrib.auth", "django.contrib.contenttypes", "django.contrib.sessions", "musica"):
            if must not in settings.INSTALLED_APPS:
                ok = False
                self.stdout.write(self.style.ERROR(f"- Falta en INSTALLED_APPS: {must}"))
        if ok:
            self.stdout.write(self.style.SUCCESS("✔ INSTALLED_APPS mínimos OK."))

        # LOGIN_URL coherencia básica (si es ruta personalizada)
        login_url = getattr(settings, "LOGIN_URL", None)
        if login_url:
            if not login_url.startswith("/"):
                self.stdout.write(self.style.WARNING(f"- LOGIN_URL debería ser una ruta (empezar con '/'): {login_url}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"✔ LOGIN_URL configurado: {login_url}"))

        # Idioma / Zona horaria (sugerencias, no errores)
        if settings.LANGUAGE_CODE not in ("es", "es-ar"):
            self.stdout.write(self.style.WARNING(f"- LANGUAGE_CODE es '{settings.LANGUAGE_CODE}'. Sugerido: 'es' o 'es-ar'."))
        if settings.TIME_ZONE in ("UTC", "Etc/UTC"):
            self.stdout.write(self.style.WARNING("- TIME_ZONE es 'UTC'. Si estás en Argentina, sugerido: 'America/Argentina/Buenos_Aires'."))
