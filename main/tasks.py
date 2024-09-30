# main/tasks.py
from celery import shared_task
from django.utils import timezone
from .models import Livre ,Location

@shared_task
def update_livre_disponibilite():
    # Récupère tous les livres
    livres = Livre.objects.all()
    now = timezone.now()

    for livre in livres:
        # Vérifie s'il y a des locations actives pour ce livre
        locations_actives = livre.location_set.filter(date_fin__gte=now)
        livre_disponible = not locations_actives.exists()

        # Si le statut a changé, le mettre à jour
        if livre.disponible != livre_disponible:
            livre.disponible = livre_disponible
            livre.save()

@shared_task
def update_locations_status():
    now = timezone.now()
    # Met à jour les locations en cours
    Location.objects.filter(date_debut__lte=now, date_fin__gt=now, statut='Réservé').update(statut='En cours')
    # Met à jour les locations terminées
    Location.objects.filter(date_fin__lt=now, statut__in=['Réservé', 'En cours']).update(statut='Terminé')
