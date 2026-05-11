from django.contrib import admin
from django.urls import include, path
from bornes.views import login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('bornes/', include('bornes.urls')),
    path('', login_view, name='connexion'),  # ← Changé 'login' → 'connexion'
]