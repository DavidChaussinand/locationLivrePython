from django.utils.translation import gettext_lazy as _

# main/admin.py
from django.contrib import admin
from .models import Livre
from .forms import LivreForm

@admin.register(Livre)
class LivreAdmin(admin.ModelAdmin):
    form = LivreForm
    list_display = ['titre', 'auteur', 'categorie', 'disponible']
