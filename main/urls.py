# mybookrental/main/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),  # Page d'accueil
    path('login/', views.login_view, name='login'),  # Page de connexion
    path('signup/', views.signup_view, name='signup'),  # Page d'inscription
    path('logout/', views.logout_view, name='logout'),  # Déconnexion personnalisée
    path('profile/', views.profile, name='profile'),  # Page de profil protégée

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

]