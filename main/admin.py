from django.utils.translation import gettext_lazy as _

# main/admin.py
from django.contrib import admin, messages
from .models import Livre , Topic
from .forms import LivreForm 
from .models import Message , Location ,Evenement , Inscription
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django import forms
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.urls import reverse


@admin.register(Livre)
class LivreAdmin(admin.ModelAdmin):
    form = LivreForm
    list_display = ['titre', 'auteur', 'categorie', 'disponible', 'best_seller']  # Note que c'est 'best_seller' ici
    list_editable = ['best_seller']  # Rendre best_seller éditable depuis la liste
    search_fields = ['titre', 'auteur', 'categorie']  # Pas besoin de best_seller ici pour la recherche
    list_filter = ['categorie']  # Filtrer par catégorie



class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at']
    list_filter = ['author', 'created_at']
    search_fields = ['title', 'content']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)
    
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['livre', 'user', 'date_debut', 'date_fin', 'statut']
    list_filter = ['statut', 'date_debut', 'date_fin']
    search_fields = ['livre__titre', 'user__username']
    autocomplete_fields = ['livre', 'user']  # Pour faciliter la sélection des livres et utilisateurs


admin.site.register(Topic, TopicAdmin)
admin.site.register(Message)



@admin.register(Evenement)
class EvenementAdmin(admin.ModelAdmin):
    list_display = ['titre', 'date']
    search_fields = ['titre', 'contenu']
    list_filter = ['date']



@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prenom', 'email', 'telephone', 'evenement']
    search_fields = ['nom', 'prenom', 'email']
    list_filter = ['evenement']


# Formulaire personnalisé pour l'envoi d'emails
class EmailForm(forms.Form):
    sujet = forms.CharField(max_length=255)
    message = forms.CharField(widget=forms.Textarea)

# Récupérer l'enregistrement de UserAdmin existant
class CustomUserAdmin(DefaultUserAdmin):
    actions = ['envoyer_email']

    def envoyer_email(self, request, queryset):
        if 'apply' in request.POST:
            form = EmailForm(request.POST)
            if form.is_valid():
                sujet = form.cleaned_data['sujet']
                message = form.cleaned_data['message']
                destinataires = [user.email for user in queryset if user.email]
                if destinataires:
                    send_mail(
                        sujet,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        destinataires,
                        fail_silently=False,
                    )
                    self.message_user(request, "Les e-mails ont été envoyés avec succès !")
                else:
                    self.message_user(
                        request,
                        "Aucun e-mail valide trouvé parmi les utilisateurs sélectionnés.",
                        level=messages.WARNING
                    )
                return redirect(request.get_full_path())
        else:
            form = EmailForm()
        context = {
            'form': form,
            'users': queryset,
            'action': 'envoyer_email',
            'opts': self.model._meta,
            'ACTION_CHECKBOX_NAME': ACTION_CHECKBOX_NAME,
        }
        return render(request, 'admin/send_mail.html', context)

    envoyer_email.short_description = "Envoyer un e-mail aux utilisateurs sélectionnés"



# Désenregistrer le modèle User s'il est déjà enregistré
admin.site.unregister(User)
# Réenregistrer User avec CustomUserAdmin
admin.site.register(User, CustomUserAdmin)