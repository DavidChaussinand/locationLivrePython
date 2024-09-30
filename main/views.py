

# mybookrental/main/views.py
from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm , EmailLoginForm , ContactForm , CommentaireForm ,MessageForm, LocationForm , ProlongationLocationForm
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.core.mail import send_mail
from .models import Livre , Commentaire ,Topic, Message , Location
from django.db.models import Q
from datetime import datetime
from django.utils import timezone




def home(request):
    best_sellers = Livre.objects.filter(best_seller=True)
    return render(request, 'main/home.html', {'best_sellers': best_sellers})

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
            messages.success(request, 'Votre compte a été créé avec succès !')
            login(request, user)  # Connecte automatiquement l'utilisateur après l'inscription
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
        return render(request, 'main/forum.html', {'topics': topics})
    
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




def location_livre(request, livre_id):
    livre = get_object_or_404(Livre, id=livre_id)
    return render(request, 'main/location_livre.html', {'livre': livre})


@login_required
def reserver_livre(request, livre_id):
    livre = get_object_or_404(Livre, id=livre_id)
    if not livre.disponible:
        messages.error(request, "Ce livre n'est pas disponible.")
        return redirect('livres')

    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            location = form.save(commit=False)
            location.user = request.user
            location.livre = livre
            location.save()
            livre.disponible = False
            livre.save()
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
    location = get_object_or_404(Location, id=location_id, user=request.user, statut='Réservé')
    location.delete()
    location.livre.disponible = True
    location.livre.save()
    messages.success(request, "Réservation annulée.")
    return redirect('profile')

# views.py
@login_required
def prolonger_location(request, location_id):
    location = get_object_or_404(Location, id=location_id, user=request.user)

    if request.method == 'POST':
        form = ProlongationLocationForm(request.POST, instance=location)
        if form.is_valid():
            # Seule la date de fin est modifiée
            location.date_fin = form.cleaned_data['date_fin']
            location.save()
            messages.success(request, "Location prolongée avec succès.")
            return redirect('profile')
    else:
        form = ProlongationLocationForm(instance=location)

    return render(request, 'main/prolonger_location.html', {'form': form, 'location': location})



# def mes_locations(request):
#     # Récupère les locations de l'utilisateur connecté
#     locations = Location.objects.filter(user=request.user)

#     # Filtrer les locations en cours
#     locations_en_cours = locations.filter(statut='En cours')

#     # Filtrer les locations terminées
#     locations_terminees = locations.filter(statut='Terminé')

#     context = {
#         'locations_en_cours': locations_en_cours,
#         'locations_terminees': locations_terminees,
#     }

#     return render(request, 'ton_template.html', context)


