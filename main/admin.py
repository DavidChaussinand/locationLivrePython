from django.utils.translation import gettext_lazy as _

# main/admin.py
from django.contrib import admin
from .models import Livre , Topic
from .forms import LivreForm
from .models import Message , Location ,Evenement , Inscription

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