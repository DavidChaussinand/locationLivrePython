from django.utils.translation import gettext_lazy as _

# main/admin.py
from django.contrib import admin
from .models import Livre , Topic
from .forms import LivreForm
from .models import Message

@admin.register(Livre)
class LivreAdmin(admin.ModelAdmin):
    form = LivreForm
    list_display = ['titre', 'auteur', 'categorie', 'disponible']
    search_fields = ['titre', 'auteur', 'categorie']  # Champs sur lesquels effectuer la recherche
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

admin.site.register(Topic, TopicAdmin)
admin.site.register(Message)


