from django.db.models import Count, Sum, Avg
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from .models import Borne, TypeConnecteur, SessionCharge
from .forms import SessionChargeForm, BorneStatusForm


# ── Vues d'authentification ───────────────────────────────────────────────────

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('bornes:liste')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "❌ Ce compte n'existe pas.")
            return render(request, 'bornes/login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.is_superuser:
                messages.success(request, f"Bonjour {user.username} (Administrateur)")
            else:
                messages.success(request, f"Bonjour {user.username} (Technicien)")
            return redirect('bornes:liste')
        else:
            messages.error(request, "❌ Mot de passe incorrect.")
            return render(request, 'bornes/login.html')
    
    return render(request, 'bornes/login.html')


login_view = custom_login


def logout_view(request):
    logout(request)
    messages.info(request, " Vous avez été déconnecté.")
    return redirect('bornes:login')


# ── Liste des bornes ──────────────────────────────────────────────────────────

class BorneListView(ListView):
    model               = Borne
    template_name       = 'bornes/liste.html'
    context_object_name = 'bornes'
    paginate_by         = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related('type_connecteur')
        
        if self.request.user.is_authenticated and not self.request.user.is_superuser:
            qs = qs.filter(statut='maintenance')
        
        ville = self.request.GET.get('ville', '').strip()
        if ville:
            qs = qs.filter(ville__icontains=ville)

        statut = self.request.GET.get('statut', '')
        if statut:
            qs = qs.filter(statut=statut)

        connecteur_id = self.request.GET.get('connecteur', '')
        if connecteur_id:
            qs = qs.filter(type_connecteur_id=connecteur_id)

        puissance_min = self.request.GET.get('puissance_min', '')
        if puissance_min:
            qs = qs.filter(puissance_kw__gte=puissance_min)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['connecteurs']    = TypeConnecteur.objects.all()
        ctx['statut_choices'] = Borne.STATUT_CHOICES
        ctx['params']         = self.request.GET
        ctx['is_technicien'] = self.request.user.is_authenticated and not self.request.user.is_superuser
        return ctx


# ── Détail d'une borne ────────────────────────────────────────────────────────

class BorneDetailView(DetailView):
    model               = Borne
    template_name       = 'bornes/detail.html'
    context_object_name = 'borne'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['sessions'] = self.object.sessioncharge_set.order_by('-date_debut')
        ctx['is_technicien'] = self.request.user.is_authenticated and not self.request.user.is_superuser
        ctx['status_form'] = BorneStatusForm(instance=self.object) if (self.request.user.is_authenticated and not self.request.user.is_superuser) else None
        return ctx


@login_required
def modifier_statut_borne(request, pk):
    borne = get_object_or_404(Borne, pk=pk)
    
    if request.user.is_superuser:
        messages.error(request, "Seuls les techniciens peuvent modifier le statut.")
        return redirect('bornes:detail', pk=pk)
    
    if request.method == 'POST':
        form = BorneStatusForm(request.POST, instance=borne)
        if form.is_valid():
            form.save()
            messages.success(request, f"Statut de la borne {borne.identifiant} modifié.")
    return redirect('bornes:detail', pk=pk)


# Alias pour urlpatterns
changer_statut = modifier_statut_borne


# ── Liste des connecteurs ─────────────────────────────────────────────────────

class TypeConnecteurListView(ListView):
    model               = TypeConnecteur
    template_name       = 'bornes/connecteurs.html'
    context_object_name = 'connecteurs'

    def get_queryset(self):
        if self.request.user.is_authenticated and not self.request.user.is_superuser:
            types = TypeConnecteur.objects.all()
            for t in types:
                t.nb_bornes = Borne.objects.filter(type_connecteur=t, statut='maintenance').count()
            return types
        return TypeConnecteur.objects.annotate(nb_bornes=Count('borne')).order_by('nom')


# ── Liste des sessions ────────────────────────────────────────────────────────

class SessionChargeListView(ListView):
    model               = SessionCharge
    template_name       = 'bornes/sessions.html'
    context_object_name = 'sessions'
    paginate_by         = 25

    def get_queryset(self):
        qs = SessionCharge.objects.select_related('borne')
        
        if self.request.user.is_authenticated and not self.request.user.is_superuser:
            qs = qs.filter(borne__statut='maintenance')

        borne_id = self.request.GET.get('borne', '')
        if borne_id:
            qs = qs.filter(borne_id=borne_id)

        date_debut = self.request.GET.get('date_debut', '')
        if date_debut:
            qs = qs.filter(date_debut__date__gte=date_debut)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated and self.request.user.is_superuser:
            ctx['bornes'] = Borne.objects.all()
            stats_qs = SessionCharge.objects.all()
        else:
            ctx['bornes'] = Borne.objects.filter(statut='maintenance')
            stats_qs = SessionCharge.objects.filter(borne__statut='maintenance')
        
        ctx['params'] = self.request.GET
        ctx['is_technicien'] = self.request.user.is_authenticated and not self.request.user.is_superuser

        stats = stats_qs.aggregate(
            total_sessions = Count('id'),
            total_energie  = Sum('energie_kwh'),
            duree_moyenne  = Avg('duree_minutes'),
        )
        ctx['stats'] = stats
        return ctx


# ── CRUD Sessions (admin uniquement) ─────────────────────────────────────────

class SessionChargeCreateView(UserPassesTestMixin, CreateView):
    model = SessionCharge
    form_class = SessionChargeForm
    template_name = 'bornes/session_form.html'
    success_url = reverse_lazy('bornes:sessions')
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        return redirect('bornes:liste')


class SessionChargeUpdateView(UserPassesTestMixin, UpdateView):
    model = SessionCharge
    form_class = SessionChargeForm
    template_name = 'bornes/session_form.html'
    success_url = reverse_lazy('bornes:sessions')
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        return redirect('bornes:liste')


class SessionChargeDeleteView(UserPassesTestMixin, DeleteView):
    model = SessionCharge
    template_name = 'bornes/session_confirm_delete.html'
    success_url = reverse_lazy('bornes:sessions')
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        return redirect('bornes:liste')