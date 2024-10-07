# mybookrental/main/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import  inscrire_evenement

urlpatterns = [
    path('', views.home, name='home'),  # Page d'accueil
    path('login/', views.login_view, name='login'),  # Page de connexion
    path('signup/', views.signup_view, name='signup'),  # Page d'inscription
    path('logout/', views.logout_view, name='logout'),  # Déconnexion personnalisée
    path('profile/', views.profile_view, name='profile'),  # Assurez-vous que le nom de la vue est correct.


    # URLs pour la réinitialisation de mot de passe avec des vues basées sur les fonctions
    path('password_reset/', views.password_reset, name='password_reset'),
    path('password_reset/done/', views.password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', views.password_reset_complete, name='password_reset_complete'),
    # Page de contact
    path('contact/', views.contact_view, name='contact'),
    path('livres/', views.livres_view, name='livres'),  # URL pour la page des livres
    path('livres/<int:livre_id>/', views.livre_detail, name='livre_detail'),  # URL pour le détail d'un livre
    path('forum/', views.forum_view, name='forum'),
    path('forum/topic/<int:topic_id>/', views.topic_detail, name='topic_detail'),
    
   
    path('annuler_location/<int:location_id>/', views.annuler_location, name='annuler_location'),
    path('reservation/<int:livre_id>/', views.reserver_livre, name='reservation_livre'),
    path('prolonger_location/<int:location_id>/', views.prolonger_location, name='prolonger_location'),
    path('evenement/<int:evenement_id>/inscription/', inscrire_evenement, name='inscrire_evenement'),
    path('evenement/<int:evenement_id>/generate_pdf/', views.generate_pdf, name='generate_pdf'),
    path('evenement/<int:evenement_id>/send_email/', views.send_email, name='send_email'),
]

   



