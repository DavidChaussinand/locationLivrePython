

# mybookrental/main/views.py
from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm , EmailLoginForm , ContactForm , CommentaireForm ,MessageForm, LocationForm , ProlongationLocationForm , InscriptionForm
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.core.mail import send_mail
from .models import Livre , Commentaire ,Topic, Message , Location, Evenement , Profile
from django.db.models import Q
from datetime import datetime
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import get_template
from django.core.mail import send_mail
from io import BytesIO
from reportlab.pdfgen import canvas
from django.contrib.auth.decorators import user_passes_test
from datetime import timedelta
import logging
from celery.result import AsyncResult
from django.conf import settings


from .tasks import send_reminder_email




def home(request):
    best_sellers = Livre.objects.filter(best_seller=True)
    evenements = Evenement.objects.all().order_by('-date')
    return render(request, 'main/home.html', {
        'best_sellers': best_sellers,
        'evenements': evenements,
    })

# Vue pour la page de connexion

# main/views.py
def login_view(request):
    if request.method == 'POST':
        form = EmailLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')  # Redirige vers la page de profil après connexion
            else:
                # Les messages d'erreur sont maintenant gérés dans le formulaire
                pass
        else:
            # Si le formulaire n'est pas valide, les erreurs sont déjà ajoutées
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = EmailLoginForm()
    return render(request, 'main/login.html', {'form': form})


# Vue pour la page d'inscription

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Spécifier explicitement le backend lors de la connexion
            backend = 'django.contrib.auth.backends.ModelBackend'  # Utiliser le backend par défaut ou un autre backend si nécessaire
            login(request, user, backend=backend)
            
            messages.success(request, 'Votre compte a été créé avec succès !')
            return redirect('home')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = SignUpForm()
    
    return render(request, 'main/signup.html', {'form': form})

# Vue pour la déconnexion
def logout_view(request):
    logout(request)
    return redirect('home')




# Exemple de vue protégée par authentification
@login_required
def profile(request):
    return render(request, 'main/profile.html')


def password_reset(request):
    return PasswordResetView.as_view(
        template_name='registration/password_reset_form.html'
    )(request)

def password_reset_done(request):
    return PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    )(request)

def password_reset_confirm(request, uidb64=None, token=None):
    return PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    )(request, uidb64=uidb64, token=token)

def password_reset_complete(request):
    return PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    )(request)




def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Récupérer les données du formulaire
            nom = form.cleaned_data['nom']
            prenom = form.cleaned_data['prenom']
            email = form.cleaned_data['email']
            telephone = form.cleaned_data['telephone']
            sujet = form.cleaned_data['sujet']
            message = form.cleaned_data['message']
            
            # Contenu de l'e-mail
            email_subject = f"Nouvelle demande de contact de {prenom} {nom} - {sujet}"
            email_message = f"Nom : {nom}\nPrénom : {prenom}\nE-mail : {email}\nTéléphone : {telephone}\n\nMessage:\n{message}"
            
            # Envoyer l'e-mail
            try:
                send_mail(
                    email_subject,
                    email_message,
                    'dav.chaussinand@gmail.com',  # Adresse e-mail expéditeur
                    ['dav.chaussinand@gmail.com'],  # Adresse e-mail destinataire
                    fail_silently=False,
                )
                messages.success(request, 'Votre message a été envoyé avec succès.')
                return redirect('contact')
            except Exception as e:
                messages.error(request, f"Une erreur s'est produite lors de l'envoi de votre message : {str(e)}")
    else:
        form = ContactForm()

    return render(request, 'main/contact.html', {'form': form})



def livres_view(request):
    query = request.GET.get('q', '')  # Récupère le texte de recherche
    categories = request.GET.getlist('categories')  # Récupère les catégories sélectionnées
    disponible = request.GET.get('disponible')  # Récupère la valeur de la case à cocher 'disponible'

    livres = Livre.objects.all().order_by('-id')

    if query:
        livres = livres.filter(
            Q(titre__icontains=query) | Q(auteur__icontains=query)
        )

    if categories:
        livres = livres.filter(categorie__in=categories)

    if disponible:
        livres = livres.filter(disponible=True)

    context = {
        'livres': livres,
        'categories': categories,
        'category_choices': Livre.CATEGORIES_CHOICES,
    }
    return render(request, 'main/livres.html', context)


def livre_detail(request, livre_id):
    livre = get_object_or_404(Livre, id=livre_id)
    commentaires = livre.commentaires.all()

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = CommentaireForm(request.POST)
            if form.is_valid():
                commentaire = form.save(commit=False)
                commentaire.user = request.user
                commentaire.livre = livre
                commentaire.contenu = commentaire.contenu.capitalize()
                commentaire.save()
                return redirect('livre_detail', livre_id=livre.id)
        else:
            messages.error(request, "Vous devez être connecté pour laisser un commentaire.")
            return redirect('login')

    form = CommentaireForm()
    context = {
        'livre': livre,
        'commentaires': commentaires,
        'form': form
    }
    return render(request, 'main/livre_detail.html', context)



def forum_view(request):
    topics = Topic.objects.all()
    users = User.objects.exclude(id=request.user.id)
    
    # Créer une liste associant chaque utilisateur à son profil et son statut is_connect
    user_profiles = []
    for user in users:
        profile = Profile.objects.filter(user=user).first()  # Utiliser filter pour éviter les erreurs
        user_profiles.append({'user': user, 'is_connect': profile.is_connect if profile else False})
    
    return render(request, 'main/forum.html', {
        'topics': topics,
        'user_profiles': user_profiles,  # Cette liste contient les utilisateurs et leur statut
        'users': users  # On passe également les utilisateurs pour conserver la structure du template
    })
    
def topic_detail(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    messages = topic.messages.order_by('-created_at')  # Trier par date de création descendante

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = MessageForm(request.POST)
            if form.is_valid():
                message = form.save(commit=False)
                message.topic = topic
                message.author = request.user
                message.save()
                return redirect('topic_detail', topic_id=topic.id)
        else:
            return redirect('login')

    form = MessageForm()
    return render(request, 'main/topic_detail.html', {'topic': topic, 'messages': messages, 'form': form})








@login_required
def reserver_livre(request, livre_id):
    livre = get_object_or_404(Livre, id=livre_id)
    if not livre.disponible:
        messages.error(request, "Ce livre n'est pas disponible.")
        return redirect('livre_detail', livre_id=livre.id)  # Assurez-vous que c'est bien la bonne redirection


    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            location = form.save(commit=False)
            location.user = request.user
            location.livre = livre
            location.save()
            livre.disponible = False
            livre.save()

            # Envoyer un e-mail à l'administrateur
            sujet = f"Réservation du livre : {livre.titre}"
            message = (
                f"Le livre '{livre.titre}' a été réservé par {request.user.get_full_name()} ({request.user.email}).\n\n"
                f"Date de début : {location.date_debut.strftime('%d/%m/%Y')}\n"
                f"Date de fin : {location.date_fin.strftime('%d/%m/%Y')}\n\n"
                "Cordialement,\n"
                "Le système de gestion des réservations"
            )
            admin_email = settings.DEFAULT_FROM_EMAIL  # Adresse e-mail de l'administrateur

            try:
                result = send_mail(
                    sujet,
                    message,
                    settings.DEFAULT_FROM_EMAIL,  # Adresse e-mail d'envoi
                    [admin_email],  # Liste des destinataires (ici l'administrateur)
                    fail_silently=False,
                )
                logger.info(f"E-mail de réservation envoyé avec succès. Résultat de send_mail : {result}")
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi de l'e-mail : {e}")
                messages.error(request, f"Une erreur est survenue lors de l'envoi de l'e-mail : {e}")

            messages.success(request, "Réservation effectuée avec succès.")
            return redirect('profile')
    else:
        form = LocationForm()
    return render(request, 'main/location_livre.html', {'livre': livre, 'form': form})



import logging
logger = logging.getLogger(__name__)

@login_required
def profile_view(request):
    locations = Location.objects.filter(user=request.user)
    today = timezone.now()
    logger.info(f"Locations: {locations}")
    context = {
        'locations': locations,
        'today': today
    }
    return render(request, 'main/profile.html', context)



@login_required
def annuler_location(request, location_id):
    location = get_object_or_404(Location, id=location_id, user=request.user, statut='en cours')
    location.delete()
    location.livre.disponible = True
    location.livre.save()
    messages.success(request, "Réservation annulée.")
    return redirect('profile')



@login_required
@login_required
def prolonger_location(request, location_id):
    location = get_object_or_404(Location, id=location_id, user=request.user)
    
    # Prolonger la date de fin
    location.date_fin += timedelta(days=7)

    # Annuler l'ancienne tâche de rappel si elle existe
    if location.reminder_task_id:
        task = AsyncResult(location.reminder_task_id)
        task.revoke()

    # Planifier une nouvelle tâche de rappel
    reminder_time = location.date_fin - timedelta(minutes=10)
    task = send_reminder_email.apply_async((location.id,), eta=reminder_time)

    # Sauvegarder le nouvel ID de tâche
    location.reminder_task_id = task.id
    location.save()

    messages.success(request, "Votre location a été prolongée avec succès.")
    return redirect('profile')





@login_required
def inscrire_evenement(request, evenement_id):
    evenement = get_object_or_404(Evenement, id=evenement_id)

    if request.method == 'POST':
        form = InscriptionForm(request.POST, utilisateur=request.user)
        if form.is_valid():
            inscription = form.save(commit=False)
            inscription.utilisateur = request.user
            inscription.evenement = evenement
            inscription.save()
            # Rediriger vers la page d'accueil après inscription
            return redirect('home')
    else:
        form = InscriptionForm(utilisateur=request.user)

    return redirect('home')  # Garde l'utilisateur sur la page d'accueil après l'inscription



# Vérifier si l'utilisateur est administrateur
def is_admin(user):
    return user.is_staff

# Générer un PDF pour les inscrits
@user_passes_test(is_admin)
def generate_pdf(request, evenement_id):
    evenement = Evenement.objects.get(id=evenement_id)
    inscrits = evenement.inscription_set.all()

    # Utilisation de reportlab pour générer un PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    # Créer le contenu du PDF
    p.drawString(100, 800, f"Inscrits pour l'événement : {evenement.titre}")
    y = 760
    for inscrit in inscrits:
        p.drawString(100, y, f"{inscrit.nom} {inscrit.prenom} - {inscrit.email} - {inscrit.telephone}")
        y -= 20

    p.showPage()
    p.save()

    # Envoyer le fichier PDF au navigateur
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

# Envoyer la liste par email
@user_passes_test(is_admin)
def send_email(request, evenement_id):
    evenement = Evenement.objects.get(id=evenement_id)
    inscrits = evenement.inscription_set.all()

    # Créer le contenu de l'email
    message = f"Liste des inscrits pour l'événement {evenement.titre}:\n\n"
    for inscrit in inscrits:
        message += f"{inscrit.nom} {inscrit.prenom} - {inscrit.email} - {inscrit.telephone}\n"

    # Envoi de l'email
    send_mail(
        f"Inscrits pour {evenement.titre}",
        message,
        'admin@votre-site.com',
        [request.user.email],  # Envoyer l'email à l'administrateur connecté
        fail_silently=False,
    )

    return HttpResponse("Email envoyé avec succès.")
