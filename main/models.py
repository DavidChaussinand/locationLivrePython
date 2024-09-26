from django.db import models

# Create your models here.
# main/models.py
from django.db import models
from django.contrib.auth.models import User

class Livre(models.Model):
    CATEGORIES_CHOICES = [
        ('fiction', 'Fiction'),
        ('science_fiction', 'Science-fiction'),
        ('fantasy', 'Fantasy'),
        ('biography', 'Biographie'),
        ('history', 'Histoire'),
        ('mystery', 'Mystère'),
        ('poetry', 'Poésie'),
        ('policier', 'Policier'),
        # Ajoute d'autres catégories selon tes besoins
    ]

    titre = models.CharField(max_length=200, verbose_name='Titre')
    auteur = models.CharField(max_length=100, verbose_name='Auteur')
    date_publication = models.DateField(verbose_name='Date de publication')
    disponible = models.BooleanField(default=True, verbose_name='Disponible à la location')
    prix = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, verbose_name='Prix (optionnel)')
    best_seller = models.BooleanField(default=False, verbose_name='Best-seller')
    resume = models.TextField(blank=True, verbose_name='Résumé')
    categorie = models.CharField(max_length=50, choices=CATEGORIES_CHOICES, verbose_name='Catégorie')
    couverture = models.CharField(max_length=200, blank=True, verbose_name='Nom de l\'image de couverture')  # Utilisation d'un lien vers l'image
    description = models.TextField(blank=True, verbose_name='Description')  # Champ pour le résumé du livre
    

    def __str__(self):
        return self.titre
    

class Commentaire(models.Model):
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE, related_name='commentaires')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contenu = models.TextField(verbose_name="Commentaire")
    date = models.DateTimeField(auto_now_add=True)
    note = models.DecimalField(max_digits=2, decimal_places=1, default=0)  # Note ajoutée


    def __str__(self):
        return f"Commentaire de {self.user.username} sur {self.livre.titre}"
