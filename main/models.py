from django.db import models

# Create your models here.
# main/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime


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



class Topic(models.Model):
    title = models.CharField(max_length=200, verbose_name="Titre")
    content = models.TextField(verbose_name="Contenu")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Auteur")

    def __str__(self):
        return self.title
    


class Message(models.Model):
    topic = models.ForeignKey('Topic', on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(verbose_name='Contenu du message')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message de {self.author.username} sur {self.topic.title}"
    




class Location(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE)
    date_debut = models.DateTimeField(default=timezone.now)
    date_fin = models.DateTimeField(default=timezone.now)
    statut = models.CharField(max_length=20, choices=[('Réservé', 'Réservé'), ('En cours', 'En cours'), ('Terminé', 'Terminé')], default='Réservé')

    def __str__(self):
        return f"{self.livre.titre} loué par {self.user.username}"
    
    def save(self, *args, **kwargs):
        now = timezone.now()
        # Vérifie si la date de fin est dépassée et met à jour le statut
        if self.date_debut <= now < self.date_fin:
            self.statut = 'En cours'
        elif now >= self.date_fin:
            self.statut = 'Terminé'
            if not self.livre.disponible:
                # Rendre le livre disponible à la fin de la location
                self.livre.disponible = True
                self.livre.save()
        super(Location, self).save(*args, **kwargs)

    @classmethod
    def update_status(cls):
        now = timezone.now()
        # Mettre à jour les locations en cours
        cls.objects.filter(date_debut__lte=now, date_fin__gt=now, statut='Réservé').update(statut='En cours')
        # Mettre à jour les locations terminées
        cls.objects.filter(date_fin__lt=now, statut__in=['Réservé', 'En cours']).update(statut='Terminé')
