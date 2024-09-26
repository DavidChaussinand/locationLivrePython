

# mybookrental/main/views.py
from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm , EmailLoginForm , ContactForm , CommentaireForm
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.core.mail import send_mail
from .models import Livre , Commentaire
from django.db.models import Q


def home(request):
    return render(request, 'main/home.html')



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
    
    livres = Livre.objects.all().order_by('-id')

    if query:
        livres = livres.filter(
            Q(titre__icontains=query) | Q(auteur__icontains=query)
        )

    if categories:
        livres = livres.filter(categorie__in=categories)

    # Passe les choix de catégorie et les catégories sélectionnées au template
    context = {
        'livres': livres,
        'categories': categories,
        'category_choices': Livre.CATEGORIES_CHOICES,  # Ajoute les choix de catégories ici
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