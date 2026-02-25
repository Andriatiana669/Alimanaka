from pathlib import Path
import os
from decouple import Config, RepositoryEnv

# =========================================================
# ENVIRONMENT
# =========================================================
DJANGO_ENV = os.getenv("DJANGO_ENV", "production")
env_file = f".env.{DJANGO_ENV}" if os.path.exists(f".env.{DJANGO_ENV}") else ".env"
config = Config(RepositoryEnv(env_file))

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================================================
# SECURITY
# =========================================================
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", cast=bool, default=False)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1"
).split(",")

# =========================================================
# APPLICATIONS
# =========================================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "corsheaders",
    "django_crontab",
    "rest_framework",

    "authentification",
    "users",
    "conges",
    "retards",
    "permissions",
    "reposmedicale",
    "ostie",
    "events",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "users.middleware.MonthlySoldeMiddleware",
]

ROOT_URLCONF = "alimanaka.urls"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = "alimanaka.wsgi.application"

AUTH_USER_MODEL = "users.User"

# =========================================================
# DATABASE
# =========================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT"),
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# =========================================================
# INTERNATIONALIZATION
# =========================================================
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Indian/Antananarivo"
USE_I18N = True
USE_TZ = True

# =========================================================
# STATIC & MEDIA
# =========================================================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "frontend" / "dist"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =========================================================
# FRONTEND / BACKEND URLS
# =========================================================
BACKEND_URL = config("BACKEND_URL")
FRONTEND_URL = config("FRONTEND_URL")

# =========================================================
# AUTHENTICATION
# =========================================================
LOGIN_URL = "/api/auth/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

AUTHENTICATION_BACKENDS = [
    "authentification.backends.KeycloakBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# =========================================================
# SESSIONS & COOKIES
# =========================================================
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_NAME = "sessionid"
SESSION_COOKIE_AGE = config("SESSION_COOKIE_AGE", cast=int, default=3600)
SESSION_COOKIE_DOMAIN = None
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", cast=bool, default=False)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = config("SESSION_COOKIE_SAMESITE", default="Lax")
SESSION_SAVE_EVERY_REQUEST = True

CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", cast=bool, default=False)
CSRF_COOKIE_SAMESITE = config("CSRF_COOKIE_SAMESITE", default="Lax")

# =========================================================
# CORS & CSRF
# =========================================================
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default=FRONTEND_URL
).split(",")

CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default=FRONTEND_URL
).split(",")

CORS_ALLOW_ALL_ORIGINS = config("CORS_ALLOW_ALL_ORIGINS", cast=bool, default=False)
CORS_ALLOW_CREDENTIALS = True

# =========================================================
# KEYCLOAK
# =========================================================
KEYCLOAK_CONFIG = {
    "BASE_URL": config("KEYCLOAK_BASE_URL"),
    "REALM": config("KEYCLOAK_REALM"),
    "CLIENT_ID": config("KEYCLOAK_CLIENT_ID"),
    "CLIENT_SECRET": config("KEYCLOAK_CLIENT_SECRET", default=""),
}

KEYCLOAK_REQUIRED_COOKIES = [
    "KC_RESTART",
    "AUTH_SESSION_ID",
    "KEYCLOAK_SESSION",
]

# =========================================================
# REST FRAMEWORK
# =========================================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# =========================================================
# CRON
# =========================================================
CRONJOBS = [
    ("0 2 * * *", "users.cron.monthly_solde_job"),
]