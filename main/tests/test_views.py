import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core import mail
from main.models import Livre , Location
from django.contrib.messages import get_messages

from unittest.mock import patch

@pytest.mark.django_db
def test_login_success(client):
    # Créer un utilisateur
    user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
    
    # Effectuer une requête POST avec les bonnes informations d'identification
    response = client.post(reverse('login'), {
        'email': 'test@example.com',
        'password': 'testpass123'
    })

    # Vérifier que l'utilisateur est redirigé vers la page de profil après connexion
    assert response.status_code == 302  # Redirection après le login
    assert response.url == reverse('profile')  # Vérifier la redirection vers 'profile'


@pytest.mark.django_db
def test_login_fail_invalid_password(client):
    # Créer un utilisateur
    user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
    
    # Effectuer une requête POST avec un mauvais mot de passe
    response = client.post(reverse('login'), {
        'email': 'test@example.com',
        'password': 'wrongpass'
    })

    # Vérifier que l'utilisateur n'est pas redirigé et reste sur la page de connexion
    assert response.status_code == 200  # Aucun redirection, reste sur la même page
    assert "Le mot de passe est incorrect." in response.content.decode()


@pytest.mark.django_db
def test_login_empty_form(client):
    # Effectuer une requête POST avec un formulaire vide
    response = client.post(reverse('login'), {
        'email': '',
        'password': ''
    })

    # Vérifier que les messages d'erreur sont générés
    assert response.status_code == 200  # Pas de redirection
    assert "Ce champ est obligatoire." in response.content.decode()



@pytest.mark.django_db
def test_contact_form_valid_submission(client):
    """
    Teste que le formulaire de contact est soumis avec succès et que l'e-mail est envoyé.
    """
    # Données valides pour le formulaire
    form_data = {
        'nom': 'Chaussinand',
        'prenom': 'David',
        'email': 'david@example.com',
        'telephone': '0123456789',
        'sujet': 'gestion_compte',
        'message': 'Bonjour, je souhaite gérer mon compte.',
    }

    # Effectuer une requête POST avec les données du formulaire
    response = client.post(reverse('contact'), data=form_data)

    # Vérifier la redirection après succès de l'envoi
    assert response.status_code == 302  # Redirection après succès
    assert response.url == reverse('contact')  # Redirige vers la page de contact

    # Vérifier que l'e-mail a bien été envoyé
    assert len(mail.outbox) == 1  # 1 e-mail envoyé
    assert mail.outbox[0].subject == "Nouvelle demande de contact de David Chaussinand - gestion_compte"

    # Vérifier que le message de succès est affiché
    messages = list(get_messages(response.wsgi_request))
    assert any("Votre message a été envoyé avec succès." in str(message) for message in messages)


@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')





@pytest.mark.django_db
@patch('main.views.send_reminder_email.apply_async')
def test_location_livre_reservation_success(mock_apply_async, client, user):
    # Configurer la valeur de retour de mock_apply_async pour simuler un ID de tâche
    mock_apply_async.return_value.id = "mock_task_id"

    # Créer un livre disponible
    livre = Livre.objects.create(titre="Mon Livre", date_publication=timezone.now(), disponible=True)

    # Simuler une requête POST pour réserver le livre
    client.force_login(user)
    response = client.post(reverse('location_livre', args=[livre.id]))

    # Vérifier que la réservation a réussi
    assert response.status_code == 302  # Redirige vers le profil
    livre.refresh_from_db()
    assert not livre.disponible  # Le livre est devenu indisponible

    # Vérifier qu'une tâche de rappel a été planifiée
    assert mock_apply_async.called
    location = Location.objects.get(livre=livre, user=user)
    assert location.statut == 'En cours'
    assert location.reminder_task_id == "mock_task_id"  # Vérifier que l'ID de la tâche est correctement enregistré


@pytest.mark.django_db
def test_location_livre_non_disponible(client, user):
    # Créer un livre non disponible
    livre = Livre.objects.create(titre="Mon Livre", date_publication=timezone.now(), disponible=False)

    # Simuler une requête POST pour réserver le livre
    client.force_login(user)
    response = client.post(reverse('location_livre', args=[livre.id]))

    # Vérifier que l'utilisateur est redirigé car le livre n'est pas disponible
    assert response.status_code == 302
    assert response.url == reverse('livre_detail', args=[livre.id])

    # Vérifier que le livre est toujours indisponible
    livre.refresh_from_db()
    assert not livre.disponible

