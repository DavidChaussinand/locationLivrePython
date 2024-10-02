import pytest
from django.utils import timezone
from main.tasks import update_livre_disponibilite
from main.models import Livre, Location
from django.contrib.auth.models import User
from main.tasks import send_reminder_email, update_locations_status  # Ajout des imports manquants
import logging

@pytest.mark.django_db
def test_update_livre_disponibilite_livre_disponible():
    """
    Teste que les livres sans locations actives sont marqués comme disponibles.
    """
    # Créer un livre sans location active
    livre = Livre.objects.create(titre="Livre Disponible", date_publication=timezone.now(), disponible=False)

    # Exécuter la tâche de mise à jour
    update_livre_disponibilite()

    # Vérifier que le livre est maintenant marqué comme disponible
    livre.refresh_from_db()
    assert livre.disponible is True


@pytest.mark.django_db
def test_update_livre_disponibilite_livre_indisponible():
    """
    Teste que les livres avec des locations actives sont marqués comme indisponibles.
    """
    # Créer un utilisateur pour l'associer à la location
    user = User.objects.create(username="testuser", email="test@example.com", password="testpass123")
    
    # Créer un livre et une location active
    livre = Livre.objects.create(titre="Livre Indisponible", date_publication=timezone.now(), disponible=True)
    Location.objects.create(livre=livre, user=user, date_debut=timezone.now(), date_fin=timezone.now() + timezone.timedelta(days=7), statut='En cours')

    # Exécuter la tâche de mise à jour
    update_livre_disponibilite()

    # Vérifier que le livre est maintenant marqué comme indisponible
    livre.refresh_from_db()
    assert livre.disponible is False



@pytest.mark.django_db
def test_update_locations_status_updates_to_terminated():
    """
    Teste que les locations en cours dont la date de fin est passée
    sont mises à jour au statut 'Terminé'.
    """
    # Créer un utilisateur
    user = User.objects.create(username='testuser', email='test@example.com', password='testpass123')

    # Créer un livre et une location "En cours"
    livre = Livre.objects.create(titre="Livre En Cours", date_publication=timezone.now(), disponible=False)
    location = Location.objects.create(user=user, livre=livre, date_debut=timezone.now() - timezone.timedelta(days=10),
                                       date_fin=timezone.now() - timezone.timedelta(days=1), statut='En cours')

    # Appeler la tâche
    update_locations_status()

    # Vérifier que la location est bien passée à 'Terminé'
    location.refresh_from_db()
    assert location.statut == 'Terminé'




@pytest.mark.django_db
def test_update_locations_status_no_update_if_not_due():
    """
    Teste que les locations dont la date de fin n'est pas encore atteinte
    ne sont pas mises à jour.
    """
    # Créer un utilisateur
    user = User.objects.create(username='testuser', email='test@example.com', password='testpass123')

    # Créer un livre et une location toujours "En cours"
    livre = Livre.objects.create(titre="Livre Toujours En Cours", date_publication=timezone.now(), disponible=False)
    location = Location.objects.create(user=user, livre=livre, date_debut=timezone.now() - timezone.timedelta(days=5),
                                       date_fin=timezone.now() + timezone.timedelta(days=2), statut='En cours')

    # Appeler la tâche
    update_locations_status()

    # Vérifier que la location n'a pas été mise à jour
    location.refresh_from_db()
    assert location.statut == 'En cours'


@pytest.mark.django_db
def test_send_reminder_email_successful_send(mailoutbox):
    """
    Teste que l'e-mail de rappel est envoyé pour une location en cours.
    """
    # Créer un utilisateur
    user = User.objects.create(username='testuser', first_name='David', email='test@example.com', password='testpass123')

    # Créer un livre et une location
    livre = Livre.objects.create(titre="Livre En Cours", date_publication=timezone.now(), disponible=False)
    location = Location.objects.create(user=user, livre=livre, date_debut=timezone.now() - timezone.timedelta(days=3),
                                       date_fin=timezone.now() + timezone.timedelta(days=1), statut='En cours')

    # Appeler la tâche de rappel d'e-mail
    send_reminder_email(location.id)

    # Vérifier qu'un e-mail a bien été envoyé
    assert len(mailoutbox) == 1
    assert mailoutbox[0].subject == "Rappel : Votre location se termine bientôt"
    assert user.email in mailoutbox[0].to



@pytest.mark.django_db
def test_send_reminder_email_location_terminated(mailoutbox, caplog):
    """
    Teste que l'e-mail de rappel n'est pas envoyé si la location est déjà terminée.
    """
    # Créer un utilisateur
    user = User.objects.create(username='testuser', email='test@example.com', password='testpass123')

    # Créer un livre et une location terminée
    livre = Livre.objects.create(titre="Livre Terminé", date_publication=timezone.now(), disponible=True)
    location = Location.objects.create(user=user, livre=livre, date_debut=timezone.now() - timezone.timedelta(days=10),
                                       date_fin=timezone.now() - timezone.timedelta(days=1), statut='Terminé')

    # Appeler la tâche de rappel d'e-mail
    with caplog.at_level(logging.INFO):
        send_reminder_email(location.id)

    # Vérifier qu'aucun e-mail n'a été envoyé
    assert len(mailoutbox) == 0

    # Vérifier que le message de log indique que l'e-mail n'a pas été envoyé
    assert "La location" in caplog.text
    assert "est terminée" in caplog.text
