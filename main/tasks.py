# main/tasks.py
from celery import shared_task
from django.utils import timezone
from .models import Livre ,Location
from celery import shared_task
from django.core.mail import send_mail
import logging

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
    # Met à jour les locations en cours (on n'a plus besoin de filtrer par 'Réservé')
    Location.objects.filter(date_fin__lt=now, statut='En cours').update(statut='Terminé')



logger = logging.getLogger(__name__)

@shared_task
def send_reminder_email(location_id):
    try:
        logger.info(f"Tâche de rappel pour la location {location_id} commencée.")

        # Importation à l'intérieur de la tâche pour éviter l'importation circulaire
        from .models import Location

        location = Location.objects.get(id=location_id)
        user = location.user

        # Vérifier si la location est toujours valide
        if location.statut == 'Terminé':
            logger.info(f"La location {location_id} est terminée. Aucune action nécessaire.")
            return

        # Envoyer l'e-mail de rappel
        send_mail(
            subject="Rappel : Votre location se termine bientôt",
            message=f"Bonjour {user.first_name},\n\n"
                    f"Votre location pour le livre '{location.livre.titre}' se termine bientôt (le {location.date_fin}).\n"
                    f"Merci de le retourner à temps.\n\nCordialement,\nL'équipe de location de livres.",
            from_email="votre_email@example.com",
            recipient_list=[user.email],
            fail_silently=False,
        )

        logger.info(f"E-mail de rappel envoyé avec succès à {user.email} pour la location {location_id}.")

    except Location.DoesNotExist:
        logger.error(f"Location {location_id} non trouvée. Tâche de rappel annulée.")

    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'e-mail pour la location {location_id} : {e}")