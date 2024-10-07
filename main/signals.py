from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from .models import Profile

# Signaux pour la connexion/déconnexion
@receiver(user_logged_in)
def set_is_connect(sender, user, request, **kwargs):
    # Récupérer ou créer un profil pour l'utilisateur lors de la connexion
    profile, created = Profile.objects.get_or_create(user=user)
    profile.is_connect = True
    profile.save()

# Vérifier si le profil existe avant de le récupérer
@receiver(user_logged_out)
def unset_is_connect(sender, user, request, **kwargs):
    try:
        profile = Profile.objects.get(user=user)
        profile.is_connect = False
        profile.save()
    except Profile.DoesNotExist:
        # Si le profil n'existe pas, on l'ignore
        pass

# Signaux pour créer et sauvegarder le profil utilisateur
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
