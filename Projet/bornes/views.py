from django.db.models import Count, Sum, Avg
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Borne, TypeConnecteur, SessionCharge
from .forms import SessionChargeForm


# ── Liste des bornes ──────────────────────────────────────────────────────────

class BorneListView(ListView):
    model               = Borne
    template_name       = 'bornes/liste.html'
    context_object_name = 'bornes'
    paginate_by         = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related('type_connecteur')

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
        return ctx


# ── Détail d'une borne ────────────────────────────────────────────────────────

class BorneDetailView(DetailView):
    model               = Borne
    template_name       = 'bornes/detail.html'
    context_object_name = 'borne'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['sessions'] = self.object.sessioncharge_set.order_by('-date_debut')
        return ctx


# ── Liste des connecteurs ─────────────────────────────────────────────────────

class TypeConnecteurListView(ListView):
    model               = TypeConnecteur
    template_name       = 'bornes/connecteurs.html'
    context_object_name = 'connecteurs'

    def get_queryset(self):
        return TypeConnecteur.objects.annotate(
            nb_bornes=Count('borne')
        ).order_by('nom')


# ── Liste des sessions ────────────────────────────────────────────────────────

class SessionChargeListView(ListView):
    model               = SessionCharge
    template_name       = 'bornes/sessions.html'
    context_object_name = 'sessions'
    paginate_by         = 25

    def get_queryset(self):
        qs = SessionCharge.objects.select_related('borne')

        borne_id = self.request.GET.get('borne', '')
        if borne_id:
            qs = qs.filter(borne_id=borne_id)

        date_debut = self.request.GET.get('date_debut', '')
        if date_debut:
            qs = qs.filter(date_debut__date__gte=date_debut)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['bornes'] = Borne.objects.all()
        ctx['params'] = self.request.GET

        stats = SessionCharge.objects.aggregate(
            total_sessions = Count('id'),
            total_energie  = Sum('energie_kwh'),
            duree_moyenne  = Avg('duree_minutes'),
        )
        ctx['stats'] = stats
        return ctx


# ── Ajouter une session ───────────────────────────────────────────────────────

class SessionChargeCreateView(CreateView):
    model         = SessionCharge
    form_class    = SessionChargeForm
    template_name = 'bornes/session_form.html'
    success_url   = reverse_lazy('bornes:sessions')

    def form_valid(self, form):
        messages.success(self.request, "Session ajoutée avec succès.")
        return super().form_valid(form)


# ── Modifier une session ──────────────────────────────────────────────────────

class SessionChargeUpdateView(UpdateView):
    model         = SessionCharge
    form_class    = SessionChargeForm
    template_name = 'bornes/session_form.html'
    success_url   = reverse_lazy('bornes:sessions')

    def form_valid(self, form):
        messages.success(self.request, "Session modifiée avec succès.")
        return super().form_valid(form)


# ── Supprimer une session ─────────────────────────────────────────────────────

class SessionChargeDeleteView(DeleteView):
    model         = SessionCharge
    template_name = 'bornes/session_confirm_delete.html'
    success_url   = reverse_lazy('bornes:sessions')

    def form_valid(self, form):
        messages.success(self.request, "Session supprimée avec succès.")
        return super().form_valid(form)