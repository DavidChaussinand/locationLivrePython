# main/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,  get_user_model
from .models import Commentaire , Livre , Message , Location , Inscription

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Veuillez entrer votre prénom.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Veuillez entrer votre nom.')
    email = forms.EmailField(required=True, help_text="Veuillez entrer une adresse e-mail valide.")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        labels = {
            'username': 'Nom d’utilisateur',
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'email': 'Adresse e-mail',
            'password1': 'Mot de passe',
            'password2': 'Confirmer le mot de passe',
        }
        help_texts = {
            'username': None,  # Supprimer le texte d'aide par défaut
            'password1': None,  # Supprimer le texte d'aide pour le mot de passe
            'password2': None, 
        }

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        # Supprimer les messages d'aide par défaut
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user




User = get_user_model()

class EmailLoginForm(forms.Form):
    email = forms.EmailField(label="Adresse e-mail", required=True)
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe", required=True)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cette adresse e-mail n'est pas reconnue.")
        return email

    def clean_password(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        # Si l'email est valide, vérifier le mot de passe
        if email and password:
            user = authenticate(username=email, password=password)
            if email and User.objects.filter(email=email).exists():
                if not user:
                    raise forms.ValidationError("Le mot de passe est incorrect.")
        return password
    

class ContactForm(forms.Form):
    NOM_CHOIX_MOTIF = [
        ('gestion_compte', 'Gestion de compte'),
        ('reservation_livre', 'Réservation de livre'),
        ('achat_livre', 'Achat de livre'),
        ('gestion_commande', 'Gestion de commande'),
        ('autres', 'Autres'),
    ]

    nom = forms.CharField(max_length=100, label='Nom')
    prenom = forms.CharField(max_length=100, label='Prénom')
    email = forms.EmailField(label='Adresse e-mail')
    telephone = forms.CharField(
        label='Numéro de téléphone', 
        required=False, 
        widget=forms.TextInput(attrs={'placeholder': 'ex: 0123456789'})  # Ajoute un placeholder pour indiquer le format attendu
    )
    sujet = forms.ChoiceField(choices=NOM_CHOIX_MOTIF, label='Motif de la demande')
    message = forms.CharField(widget=forms.Textarea, label='Contenu')

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if telephone:
            if not telephone.isdigit():
                raise forms.ValidationError("Le numéro doit comporter uniquement des chiffres.")
            if len(telephone) != 10:
                raise forms.ValidationError("Le numéro doit comporter exactement 10 chiffres.")
        return telephone

    def clean_message(self):
        message = self.cleaned_data.get('message')
        if len(message) < 20:
            raise forms.ValidationError("Le contenu du message doit comporter au moins 20 caractères.")
        return message
    


class CommentaireForm(forms.ModelForm):
    class Meta:
        model = Commentaire
        fields = ['contenu', 'note']
        widgets = {
            'contenu': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'note': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.5, 'min': 0, 'max': 5}),
        }
        labels = {
            'contenu': 'Votre avis',
            'note': 'Note (0 à 5)',
        }

    def clean_note(self):
        note = self.cleaned_data.get('note')
        if note < 0 or note > 5:
            raise forms.ValidationError("La note doit être comprise entre 0 et 5.")
        return note


class LivreForm(forms.ModelForm):
    image_upload = forms.ImageField(required=False, label="Télécharger une image")

    class Meta:
        model = Livre
        fields = '__all__'

    def save(self, commit=True):
        livre = super().save(commit=False)
        if self.cleaned_data.get('image_upload'):
            image = self.cleaned_data['image_upload']
            image_name = f"couvertures/{image.name}"
            image_path = f"media/{image_name}"
            
            # Sauvegarde du fichier
            with open(image_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
            
            # Mise à jour du champ couverture
            livre.couverture = image_name
        
        if commit:
            livre.save()
        return livre
    
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Écris ton message ici...'}),
        }



class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['date_debut', 'date_fin']
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'type': 'date'}),
        }
    


class ProlongationLocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['date_fin']
        widgets = {
            'date_fin': forms.DateInput(attrs={'type': 'date'}),
        }


class InscriptionForm(forms.ModelForm):
    class Meta:
        model = Inscription
        fields = ['nom', 'prenom', 'email', 'telephone']

    def __init__(self, *args, **kwargs):
        utilisateur = kwargs.pop('utilisateur', None)
        super().__init__(*args, **kwargs)
        if utilisateur:
            self.fields['nom'].initial = utilisateur.first_name
            self.fields['prenom'].initial = utilisateur.last_name
            self.fields['email'].initial = utilisateur.email



