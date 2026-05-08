from django.urls import path
from .views import (
    BorneListView,
    BorneDetailView,
    TypeConnecteurListView,
    SessionChargeListView,
    SessionChargeCreateView,
    SessionChargeUpdateView,
    SessionChargeDeleteView,
)

app_name = 'bornes'

urlpatterns = [
    path('',                             BorneListView.as_view(),           name='liste'),
    path('<int:pk>/',                    BorneDetailView.as_view(),          name='detail'),
    path('connecteurs/',                 TypeConnecteurListView.as_view(),   name='connecteurs'),
    path('sessions/',                    SessionChargeListView.as_view(),    name='sessions'),
    path('sessions/ajouter/',            SessionChargeCreateView.as_view(),  name='session_ajouter'),
    path('sessions/<int:pk>/modifier/',  SessionChargeUpdateView.as_view(),  name='session_modifier'),
    path('sessions/<int:pk>/supprimer/', SessionChargeDeleteView.as_view(),  name='session_supprimer'),
]