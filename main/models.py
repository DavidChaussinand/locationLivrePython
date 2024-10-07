from django.db import models

# Create your models here.
# main/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from datetime import timedelta
from celery.result import AsyncResult


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
    statut = models.CharField(
        max_length=20,
        choices=[('En cours', 'En cours'), ('Terminé', 'Terminé')],
        default='En cours'
    )
    reminder_task_id = models.CharField(max_length=255, null=True, blank=True)  # Stocke l'ID de la tâche

    def save(self, *args, **kwargs):
        # Vérifier si la location existe déjà dans la base de données (édition)
        if self.pk:
            # Récupérer l'ancienne instance avant modification
            old_location = Location.objects.get(pk=self.pk)

            # Si la date de fin a changé, replanifier la tâche de rappel
            if old_location.date_fin != self.date_fin:
                # Annuler la tâche de rappel précédente si elle existe
                if self.reminder_task_id:
                    task = AsyncResult(self.reminder_task_id)
                    task.revoke()

                # Importer la tâche ici pour éviter l'import circulaire
                from .tasks import send_reminder_email

                # Planifier une nouvelle tâche de rappel 10 minutes avant la nouvelle date de fin
                reminder_time = self.date_fin - timedelta(minutes=10)

                # Utiliser datetime.timezone pour UTC
                from datetime import timezone as dt_timezone
                reminder_time_utc = reminder_time.astimezone(dt_timezone.utc)

                # Planifier la nouvelle tâche
                task = send_reminder_email.apply_async((self.id,), eta=reminder_time_utc)
                self.reminder_task_id = task.id

        else:  # Cas de la création d'une nouvelle location
            # Importer la tâche ici pour éviter l'import circulaire
            from .tasks import send_reminder_email

            # Planifier une tâche de rappel 10 minutes avant la date de fin
            reminder_time = self.date_fin - timedelta(minutes=10)

            # Utiliser datetime.timezone pour UTC
            from datetime import timezone as dt_timezone
            reminder_time_utc = reminder_time.astimezone(dt_timezone.utc)

            # Planifier la tâche
            task = send_reminder_email.apply_async((self.id,), eta=reminder_time_utc)
            self.reminder_task_id = task.id

        super(Location, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.reminder_task_id:
            task = AsyncResult(self.reminder_task_id)
            task.revoke()
        super(Location, self).delete(*args, **kwargs)


        
class Evenement(models.Model):
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.titre


class Inscription(models.Model):
    evenement = models.ForeignKey(Evenement, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    email = models.EmailField()
    telephone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.utilisateur.username} - {self.evenement.titre}"
    


class MessageTchat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)  # Utilise timezone.now comme valeur par défaut

    def __str__(self):
        if self.recipient:
            return f'{self.user.username} to {self.recipient.username}: {self.content}'
        return f'{self.user.username}: {self.content}'
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_connect = models.BooleanField(default=False)  # Champ pour indiquer si l'utilisateur est connecté ou non