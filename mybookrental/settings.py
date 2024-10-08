"""
Django settings for mybookrental project.

Generated by 'django-admin startproject' using Django 5.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# settings.py
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'main/static']


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-hw+8-eljqc@u0h5-)gmo_+(6g2p-*q)2gmwww7pd&)j7#l%rtw'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'main.apps.MainConfig',
]

ASGI_APPLICATION = 'mybookrental.asgi.application'


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mybookrental.urls'

# settings.py

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'main/templates'],  # Assure-toi que le chemin vers ton dossier de templates est correct
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]


WSGI_APPLICATION = 'mybookrental.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# mybookrental/settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # Utilise 'mysql' pour MySQL/MariaDB
        'NAME': 'mybookrental',  # Nom de la base de données que tu as créée
        'USER': 'root',  # Utilisateur de la base de données
        'PASSWORD': '',  # Mot de passe de l'utilisateur root (laisse vide si aucun mot de passe)
        'HOST': '127.0.0.1',  # Adresse du serveur de base de données
        'PORT': '3306',  # Port de connexion MySQL/MariaDB
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",  # Option pour MariaDB (recommandé)
            'charset': 'utf8mb4',
        },
    }
}

# mybookrental/settings.py
AUTHENTICATION_BACKENDS = [
    'main.backends.EmailAuthBackend',  # Ajoute ton backend personnalisé ici
    'django.contrib.auth.backends.ModelBackend',
]


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'fr'
TIME_ZONE = 'Europe/Paris'

USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



LOGIN_URL = '/login/'  # URL vers laquelle les utilisateurs non connectés seront redirigés


# mybookrental/settings.py
LOGIN_REDIRECT_URL = '/profile/'  # Redirige vers la page de profil après connexion


# Configuration des messages
from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',  # Associe le niveau d'erreur avec 'danger' pour Bootstrap
}

import environ


# Initialise l'environnement
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))



# Utilisation des variables d'environnement
EMAIL_BACKEND = env('EMAIL_BACKEND')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')



# Dossier pour les fichiers uploadés (images)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Configuration du courtier de messages (ici, nous utilisons Redis)
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Utiliser la timezone de Django pour Celery
CELERY_TIMEZONE = TIME_ZONE  # Assurez-vous que TIME_ZONE est bien défini

# Configuration de la tâche périodique
CELERY_BEAT_SCHEDULE = {
    'update-livre-disponibilite': {
        'task': 'main.tasks.update_livre_disponibilite',
        'schedule': 60.0,  # Toutes les 1 minutes (60 secondes)
    },
    'update-locations-status-every-minute': {
        'task': 'main.tasks.update_locations_status',
        'schedule': 60.0,  # Toutes les minutes
    },
}


# Configuration de la journalisation
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'main': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}


CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],  # Assure-toi que Redis tourne
        },
    },
}