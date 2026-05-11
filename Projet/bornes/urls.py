from django.urls import path
from . import views

app_name = 'bornes'

urlpatterns = [
    path('', views.BorneListView.as_view(), name='liste'),
    path('borne/<int:pk>/', views.BorneDetailView.as_view(), name='detail'),
    path('borne/<int:pk>/changer-statut/', views.changer_statut, name='changer_statut'),
    path('connecteurs/', views.TypeConnecteurListView.as_view(), name='connecteurs'),
    path('sessions/', views.SessionChargeListView.as_view(), name='sessions'),
    path('sessions/ajouter/', views.SessionChargeCreateView.as_view(), name='session_ajouter'),
    path('sessions/<int:pk>/modifier/', views.SessionChargeUpdateView.as_view(), name='session_modifier'),
    path('sessions/<int:pk>/supprimer/', views.SessionChargeDeleteView.as_view(), name='session_supprimer'),
    path('login/', views.login_view, name='login'),  # ← GARDE CELUI-CI
    path('logout/', views.logout_view, name='logout'),
]