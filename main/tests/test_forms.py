import pytest
from main.forms import SignUpForm ,EmailLoginForm , ContactForm , CommentaireForm , LivreForm , ProlongationLocationForm , LocationForm , MessageForm
from django.contrib.auth.models import User
from django.utils import timezone


@pytest.mark.django_db
def test_signup_form_valid():
    """
    Teste la validité du formulaire d'inscription avec des données valides.
    """
    form_data = {
        'username': 'newuser',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'johndoe@example.com',
        'password1': 'strongpassword123',
        'password2': 'strongpassword123'
    }
    form = SignUpForm(data=form_data)
    
    assert form.is_valid()  # Vérifie que le formulaire est valide
    user = form.save()
    assert user.username == 'newuser'
    assert user.email == 'johndoe@example.com'



@pytest.mark.django_db
def test_signup_form_password_mismatch():
    """
    Teste la détection d'une erreur lorsque les mots de passe ne correspondent pas.
    """
    form_data = {
        'username': 'newuser',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'johndoe@example.com',
        'password1': 'strongpassword123',
        'password2': 'differentpassword'
    }
    form = SignUpForm(data=form_data)
    
    assert not form.is_valid()  # Vérifie que le formulaire est invalide
    assert 'password2' in form.errors  # Vérifie que l'erreur concerne le champ 'password2'




@pytest.mark.django_db
def test_email_login_form_valid():
    """
    Teste la validité du formulaire de connexion avec des données valides.
    """
    user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
    
    form_data = {'email': 'test@example.com', 'password': 'password123'}
    form = EmailLoginForm(data=form_data)
    
    assert form.is_valid()  # Le formulaire doit être valide



@pytest.mark.django_db
def test_email_login_form_invalid_email():
    """
    Teste que le formulaire génère une erreur si l'e-mail n'est pas reconnu.
    """
    form_data = {'email': 'nonexistent@example.com', 'password': 'password123'}
    form = EmailLoginForm(data=form_data)
    
    assert not form.is_valid()  # Le formulaire ne doit pas être valide
    assert 'email' in form.errors  # L'erreur doit être liée au champ 'email'



@pytest.mark.django_db
def test_contact_form_valid():
    """
    Teste la validité du formulaire de contact avec des données valides.
    """
    form_data = {
        'nom': 'Doe',
        'prenom': 'John',
        'email': 'johndoe@example.com',
        'telephone': '0123456789',
        'sujet': 'reservation_livre',
        'message': 'Je voudrais réserver un livre.'
    }
    form = ContactForm(data=form_data)
    
    assert form.is_valid()  # Le formulaire doit être valide




@pytest.mark.django_db
def test_contact_form_message_too_short():
    """
    Teste la détection d'une erreur lorsque le message est trop court.
    """
    form_data = {
        'nom': 'Doe',
        'prenom': 'John',
        'email': 'johndoe@example.com',
        'telephone': '0123456789',
        'sujet': 'reservation_livre',
        'message': 'Trop court'
    }
    form = ContactForm(data=form_data)
    
    assert not form.is_valid()  # Le formulaire ne doit pas être valide
    assert 'message' in form.errors  # L'erreur doit concerner le champ 'message'



@pytest.mark.django_db
def test_commentaire_form_valid():
    """
    Teste la validité du formulaire de commentaire avec une note valide.
    """
    form_data = {
        'contenu': 'Très bon livre',
        'note': 4.5
    }
    form = CommentaireForm(data=form_data)
    
    assert form.is_valid()  # Le formulaire doit être valide



@pytest.mark.django_db
def test_commentaire_form_invalid_note():
    """
    Teste que le formulaire génère une erreur si la note est hors des limites (moins de 0 ou plus de 5).
    """
    form_data = {
        'contenu': 'Pas terrible',
        'note': 6.0  # Note hors des limites
    }
    form = CommentaireForm(data=form_data)
    
    assert not form.is_valid()  # Le formulaire ne doit pas être valide
    assert 'note' in form.errors  # L'erreur doit concerner le champ 'note'
    

@pytest.mark.django_db
def test_livre_form_without_image():
    """
    Vérifie que le formulaire LivreForm peut créer un livre sans télécharger d'image.
    """
    form_data = {
        'titre': 'Mon livre',
        'auteur': 'Auteur Exemple',
        'date_publication': timezone.now().date(),
        'categorie': 'fiction',
        'disponible': True
    }
    form = LivreForm(data=form_data)

    assert form.is_valid()  # Le formulaire doit être valide sans image
    livre = form.save()
    assert livre.couverture == ''  # Aucun fichier image ne doit être associé


@pytest.mark.django_db
def test_message_form_valid():
    """
    Vérifie que le formulaire MessageForm est valide avec un contenu.
    """
    form_data = {'content': 'Ceci est un message valide.'}
    form = MessageForm(data=form_data)

    assert form.is_valid()  # Le formulaire doit être valide



@pytest.mark.django_db
def test_message_form_empty_content():
    """
    Vérifie que le formulaire MessageForm échoue si le contenu est vide.
    """
    form_data = {'content': ''}
    form = MessageForm(data=form_data)

    assert not form.is_valid()  # Le formulaire ne doit pas être valide
    assert 'content' in form.errors  # Le champ 'content' doit avoir une erreur



@pytest.mark.django_db
def test_prolongation_form_valid():
    """
    Vérifie que le formulaire ProlongationLocationForm fonctionne correctement avec une nouvelle date de fin.
    """
    form_data = {'date_fin': (timezone.now().date() + timezone.timedelta(days=10)).isoformat()}
    form = ProlongationLocationForm(data=form_data)

    assert form.is_valid()  # Le formulaire doit être valide

