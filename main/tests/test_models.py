import pytest
from django.contrib.auth.models import User
from main.models import Livre , Commentaire , Topic , Message ,Evenement , Location , Inscription
from django.utils import timezone
from datetime import date
from unittest.mock import patch , MagicMock
from celery.result import AsyncResult

@pytest.mark.django_db
def test_livre_disponible():
    # Crée un livre avec une date de publication
    livre = Livre.objects.create(
        titre="La peste",
        disponible=True,
        date_publication=timezone.now()  # Ajout de la date de publication
    )
    
    assert livre.disponible is True


# 1. Test de la création d'un commentaire
@pytest.mark.django_db
def test_creation_commentaire():
    # Création d'un utilisateur et d'un livre
    user = User.objects.create(username="testuser")
    livre = Livre.objects.create(titre="Livre Test", disponible=True, date_publication=timezone.now())

    # Création d'un commentaire
    commentaire = Commentaire.objects.create(livre=livre, user=user, contenu="Super livre", note=4.5)

    # Vérification que le commentaire a été créé avec succès
    assert commentaire.contenu == "Super livre"
    assert commentaire.note == 4.5
    assert commentaire.livre == livre
    assert commentaire.user == user

# 2. Test de la relation livre -> commentaires (related_name)
@pytest.mark.django_db
def test_livre_commentaires_relation():
    # Création d'un utilisateur et d'un livre
    user = User.objects.create(username="testuser")
    livre = Livre.objects.create(titre="Livre Test", disponible=True, date_publication=timezone.now())

    # Ajout de deux commentaires au livre
    Commentaire.objects.create(livre=livre, user=user, contenu="Excellent", note=5.0)
    Commentaire.objects.create(livre=livre, user=user, contenu="Pas mal", note=3.0)

    # Vérification que les commentaires sont liés au livre
    assert livre.commentaires.count() == 2
    assert livre.commentaires.first().contenu == "Excellent"

# 3. Test de la note par défaut du commentaire
@pytest.mark.django_db
def test_default_comment_note():
    # Création d'un utilisateur et d'un livre
    user = User.objects.create(username="testuser")
    livre = Livre.objects.create(titre="Livre Test", disponible=True, date_publication=timezone.now())

    # Création d'un commentaire sans préciser la note
    commentaire = Commentaire.objects.create(livre=livre, user=user, contenu="Commentaire sans note")

    # Vérification que la note par défaut est 0
    assert commentaire.note == 0.0

@pytest.mark.django_db
def test_livre_creation():
    """Test de la création d'un livre avec succès."""
    livre = Livre.objects.create(
        titre="Le Seigneur des Anneaux",
        auteur="J.R.R. Tolkien",
        date_publication=date(1954, 7, 29),
        disponible=True,
        prix=25.99,
        best_seller=True,
        resume="Une grande épopée fantastique",
        categorie="fantasy",
        couverture="seigneur_des_anneaux.jpg",
        description="Un roman incontournable de la fantasy"
    )
    assert livre.titre == "Le Seigneur des Anneaux"
    assert livre.disponible is True
    assert livre.best_seller is True

@pytest.mark.django_db
def test_livre_categorie_choix():
    """Test pour vérifier que la catégorie du livre est correctement enregistrée."""
    livre = Livre.objects.create(
        titre="1984",
        auteur="George Orwell",
        date_publication=date(1949, 6, 8),
        categorie="science_fiction"
    )
    assert livre.categorie == "science_fiction"
    assert livre.categorie in dict(Livre.CATEGORIES_CHOICES)

@pytest.mark.django_db
def test_livre_disponibilite_false():
    """Test pour vérifier que la disponibilité du livre peut être définie sur False."""
    livre = Livre.objects.create(
        titre="Moby Dick",
        auteur="Herman Melville",
        date_publication=date(1851, 10, 18),
        disponible=False
    )
    assert livre.disponible is False

@pytest.mark.django_db
def test_livre_prix_optionnel():
    """Test pour vérifier que le prix est optionnel et peut être null."""
    livre = Livre.objects.create(
        titre="Les Misérables",
        auteur="Victor Hugo",
        date_publication=date(1862, 4, 3),
        disponible=True,
        prix=None  # Prix optionnel laissé à None
    )
    assert livre.prix is None
    assert livre.disponible is True


@pytest.mark.django_db
def test_topic_creation():
    """Test pour vérifier la création d'un topic avec succès."""
    user = User.objects.create_user(username="john_doe", password="password123")
    topic = Topic.objects.create(
        title="Discussion sur Django",
        content="Django est un framework fantastique pour le développement web.",
        author=user
    )
    assert topic.title == "Discussion sur Django"
    assert topic.content == "Django est un framework fantastique pour le développement web."
    assert topic.author == user

@pytest.mark.django_db
def test_topic_auto_now_add_created_at():
    """Test pour vérifier que la date de création est automatiquement ajoutée lors de la création."""
    user = User.objects.create_user(username="jane_doe", password="password123")
    topic = Topic.objects.create(
        title="Nouvelle discussion",
        content="Contenu de la discussion.",
        author=user
    )
    assert topic.created_at is not None
    assert timezone.now() >= topic.created_at  # Vérifie que la date de création est avant ou égale au moment présent

@pytest.mark.django_db
def test_topic_str_representation():
    """Test pour vérifier la méthode __str__ du modèle Topic."""
    user = User.objects.create_user(username="sam_doe", password="password123")
    topic = Topic.objects.create(
        title="Titre de Test",
        content="Contenu test pour vérifier la représentation en chaîne.",
        author=user
    )
    assert str(topic) == "Titre de Test"




@pytest.mark.django_db
def test_create_message():
    """
    Ce test vérifie qu'un message peut être créé correctement avec un auteur et un topic associés.
    """
    # Création d'un utilisateur
    user = User.objects.create(username='user1')
    
    # Création d'un topic
    topic = Topic.objects.create(title="Topic 1", content="Contenu du topic", author=user)
    
    # Création du message lié au topic et à l'utilisateur
    message = Message.objects.create(topic=topic, author=user, content="Contenu du message")
    
    # Vérification que le message a bien été créé et que les champs sont corrects
    assert message.content == "Contenu du message"
    assert message.author == user
    assert message.topic == topic

@pytest.mark.django_db
def test_message_str_representation():
    """
    Ce test vérifie que la méthode __str__ du modèle Message renvoie la chaîne correcte.
    """
    # Création d'un utilisateur et d'un topic
    user = User.objects.create(username='user2')
    topic = Topic.objects.create(title="Topic 2", content="Contenu du topic", author=user)
    
    # Création d'un message
    message = Message.objects.create(topic=topic, author=user, content="Contenu du message")
    
    # Vérification que la méthode __str__ renvoie le bon format de chaîne
    assert str(message) == f"Message de {user.username} sur {topic.title}"


@pytest.mark.django_db
def test_related_topic_messages():
    """
    Ce test vérifie que plusieurs messages peuvent être associés à un même topic.
    """
    # Création d'un utilisateur et d'un topic
    user = User.objects.create(username='user3')
    topic = Topic.objects.create(title="Topic 3", content="Contenu du topic", author=user)
    
    # Création de deux messages associés au même topic
    Message.objects.create(topic=topic, author=user, content="Premier message")
    Message.objects.create(topic=topic, author=user, content="Deuxième message")
    
    # Vérification que le topic contient bien 2 messages
    assert topic.messages.count() == 2


@pytest.mark.django_db
def test_create_location():
    """
    Ce test vérifie qu'une location peut être créée correctement avec un utilisateur et un livre associés. ATTENTION , il faut lancer le serveur REDIS pour le test
    """
    # Créer un utilisateur et un livre
    user = User.objects.create(username='user1')
    livre = Livre.objects.create(titre="Le livre", date_publication=timezone.now())

    # Créer une location
    location = Location.objects.create(user=user, livre=livre, date_debut=timezone.now(), date_fin=timezone.now() + timezone.timedelta(days=7))

    # Vérification des attributs de la location
    assert location.user == user
    assert location.livre == livre
    assert location.statut == 'Réservé'

@pytest.mark.django_db
@patch('main.tasks.send_reminder_email.apply_async')
def test_save_location_schedules_task(mock_apply_async):
    """
    Ce test vérifie qu'une tâche de rappel est planifiée lors de la création d'une nouvelle location.
    """
    # Définir un ID de tâche factice pour le mock
    mock_apply_async.return_value.id = 'fake-task-id'

    user = User.objects.create(username='user2')
    livre = Livre.objects.create(titre="Le livre", date_publication=timezone.now())

    # Créer une location et s'assurer que la tâche de rappel est bien planifiée
    location = Location.objects.create(
        user=user, 
        livre=livre, 
        date_debut=timezone.now(), 
        date_fin=timezone.now() + timezone.timedelta(days=7)
    )

    # Vérifier que la tâche a été lancée
    mock_apply_async.assert_called_once()

    # Vérifier que l'ID de la tâche est correctement sauvegardé
    assert location.reminder_task_id == 'fake-task-id'

    # Vérification des attributs de la location
    assert location.user == user
    assert location.livre == livre
    assert location.statut == 'Réservé'


@pytest.mark.django_db
def test_location_date_debut():
    """
    Ce test vérifie que la date de début d'une location est bien celle par défaut.
    """
    user = User.objects.create(username='user6')
    livre = Livre.objects.create(titre="Le livre", date_publication=timezone.now())

    # Créer une location
    location = Location.objects.create(user=user, livre=livre)

    # Vérification que la date de début correspond à la date actuelle
    assert location.date_debut.date() == timezone.now().date()

@pytest.mark.django_db
@patch('main.models.AsyncResult.revoke')
def test_delete_location_cancels_task(mock_revoke):
    """
    Ce test vérifie que lors de la suppression d'une location, la tâche de rappel planifiée est annulée.
    """
    user = User.objects.create(username='user4')
    livre = Livre.objects.create(titre="Le livre", date_publication=timezone.now())

    # Créer une location
    location = Location.objects.create(user=user, livre=livre, date_debut=timezone.now(), date_fin=timezone.now() + timezone.timedelta(days=7))

    # Supprimer la location
    location.delete()

    # Vérifier que la tâche de rappel a été annulée
    assert mock_revoke.called


@pytest.mark.django_db
@patch('celery.result.AsyncResult.revoke')  # Corriger l'import ici
@patch('main.tasks.send_reminder_email.apply_async')
def test_update_location_reschedules_task(mock_apply_async, mock_revoke):
    """
    Ce test vérifie que lorsque la date de fin d'une location est modifiée, l'ancienne tâche est annulée et une nouvelle est planifiée.
    """
    # Configurer la valeur de retour de mock_apply_async pour qu'elle soit une tâche factice avec un ID valide
    mock_task = MagicMock()
    mock_task.id = 'fake-task-id'
    mock_apply_async.return_value = mock_task

    # Créer un utilisateur et un livre
    user = User.objects.create(username='user3')
    livre = Livre.objects.create(titre="Le livre", date_publication=timezone.now())

    # Créer une location
    location = Location.objects.create(user=user, livre=livre, date_debut=timezone.now(), date_fin=timezone.now() + timezone.timedelta(days=7))

    # Modifier la date de fin
    new_date_fin = timezone.now() + timezone.timedelta(days=14)
    location.date_fin = new_date_fin
    location.save()

    # Vérifier que la tâche précédente a été révoquée et une nouvelle planifiée
    assert mock_revoke.called
    assert mock_apply_async.called
    assert location.reminder_task_id == 'fake-task-id'



@pytest.mark.django_db
def test_create_evenement():
    """
    Teste la création d'un événement avec un titre, du contenu et une date.
    """
    evenement = Evenement.objects.create(
        titre="Salon du livre",
        contenu="Un événement pour tous les amateurs de lecture.",
        date=timezone.now()
    )

    # Vérifie que l'événement a été créé et que ses attributs sont corrects
    assert evenement.titre == "Salon du livre"
    assert evenement.contenu == "Un événement pour tous les amateurs de lecture."
    assert evenement.date is not None



@pytest.mark.django_db
def test_evenement_str():
    """
    Teste la méthode __str__ de la classe Evenement pour vérifier qu'elle renvoie le titre de l'événement.
    """
    evenement = Evenement.objects.create(
        titre="Conférence Python",
        contenu="Une conférence pour les passionnés de Python.",
        date=timezone.now()
    )

    # Vérifie que la méthode __str__ renvoie bien le titre
    assert str(evenement) == "Conférence Python"




@pytest.mark.django_db
def test_create_inscription():
    """
    Teste la création d'une inscription avec un utilisateur et un événement associés.
    """
    user = User.objects.create(username='user1')
    evenement = Evenement.objects.create(
        titre="Atelier d'écriture",
        contenu="Un atelier pour les écrivains amateurs.",
        date=timezone.now()
    )
    inscription = Inscription.objects.create(
        evenement=evenement,
        utilisateur=user,
        nom="Doe",
        prenom="John",
        email="john.doe@example.com",
        telephone="0123456789"
    )

    # Vérifie que l'inscription a bien été créée
    assert inscription.utilisateur == user
    assert inscription.evenement == evenement
    assert inscription.nom == "Doe"
    assert inscription.prenom == "John"
    assert inscription.email == "john.doe@example.com"
    assert inscription.telephone == "0123456789"



@pytest.mark.django_db
def test_inscription_str():
    """
    Teste la méthode __str__ de la classe Inscription pour vérifier qu'elle renvoie le format attendu.
    """
    user = User.objects.create(username='user2')
    evenement = Evenement.objects.create(
        titre="Conférence Django",
        contenu="Apprenez à développer avec Django.",
        date=timezone.now()
    )
    inscription = Inscription.objects.create(
        evenement=evenement,
        utilisateur=user,
        nom="Smith",
        prenom="Anna",
        email="anna.smith@example.com",
        telephone="0987654321"
    )

    # Vérifie que la méthode __str__ renvoie le bon format
    assert str(inscription) == f"{user.username} - {evenement.titre}"



@pytest.mark.django_db
def test_delete_event_deletes_inscriptions():
    """
    Teste que la suppression d'un événement entraîne la suppression des inscriptions associées.
    """
    user = User.objects.create(username='user3')
    evenement = Evenement.objects.create(
        titre="Rencontre d'auteurs",
        contenu="Un événement pour rencontrer des auteurs célèbres.",
        date=timezone.now()
    )
    inscription = Inscription.objects.create(
        evenement=evenement,
        utilisateur=user,
        nom="Anderson",
        prenom="Jack",
        email="jack.anderson@example.com",
        telephone="0123456789"
    )

    # Supprimer l'événement
    evenement.delete()

    # Vérifie que l'inscription a été supprimée suite à la suppression de l'événement
    assert Inscription.objects.filter(id=inscription.id).count() == 0