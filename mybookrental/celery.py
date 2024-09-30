# mybookrental/celery.py
import os
from celery import Celery

# Définit le module de paramètres par défaut pour le programme 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mybookrental.settings')

app = Celery('mybookrental')

# Charge les paramètres depuis les variables d'environnement de Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découvre automatiquement les tâches asynchrones pour tous les modules 'tasks.py' dans vos applications Django
app.autodiscover_tasks()

