from django.contrib import admin
from django.utils.html import format_html
from .models import Borne, TypeConnecteur, SessionCharge


# ── Actions personnalisées ────────────────────────────────────────────────────

@admin.action(description="Marquer comme Libre")
def marquer_libre(modeladmin, request, queryset):
    queryset.update(statut='libre')


@admin.action(description="Marquer comme Occupée")
def marquer_occupee(modeladmin, request, queryset):
    queryset.update(statut='occupee')


@admin.action(description="Marquer comme En maintenance")
def marquer_maintenance(modeladmin, request, queryset):
    queryset.update(statut='maintenance')


# ── Inline SessionCharge dans Borne ──────────────────────────────────────────

class SessionChargeInline(admin.TabularInline):
    model    = SessionCharge
    extra    = 1
    fields   = ('date_debut', 'duree_minutes', 'energie_kwh')
    ordering = ('-date_debut',)


# ── Admin TypeConnecteur ──────────────────────────────────────────────────────

@admin.register(TypeConnecteur)
class TypeConnecteurAdmin(admin.ModelAdmin):
    list_display  = ('nom', 'vitesse_charge')
    list_filter   = ('vitesse_charge',)
    search_fields = ('nom',)


# ── Admin Borne ───────────────────────────────────────────────────────────────

@admin.register(Borne)
class BorneAdmin(admin.ModelAdmin):
    inlines       = [SessionChargeInline]
    list_display  = (
        'identifiant', 'ville', 'emplacement',
        'puissance_kw', 'type_connecteur', 'statut', 'statut_badge', 'date_installation'
    )
    list_filter   = ('statut', 'type_connecteur', 'puissance_kw')
    search_fields = ('identifiant', 'ville', 'emplacement')
    ordering      = ('identifiant',)
    actions       = [marquer_libre, marquer_occupee, marquer_maintenance]
    list_editable = ('statut',)

    @admin.display(description="Aperçu statut")
    def statut_badge(self, obj):
        couleurs = {
            'libre':       ('#0d6efd', 'Libre'),
            'occupee':     ('#fd7e14', 'Occupée'),
            'maintenance': ('#6c757d', 'En maintenance'),
        }
        couleur, label = couleurs.get(obj.statut, ('#dee2e6', obj.statut))
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;'
            'border-radius:12px;font-size:12px;font-weight:600;">{}</span>',
            couleur, label
        )


# ── Admin SessionCharge ───────────────────────────────────────────────────────

@admin.register(SessionCharge)
class SessionChargeAdmin(admin.ModelAdmin):
    list_display   = (
        'borne', 'date_debut', 'duree_affichee', 'energie_kwh', 'cout_affiche'
    )
    list_filter    = ('borne', 'date_debut')
    search_fields  = ('borne__identifiant', 'borne__ville')
    ordering       = ('-date_debut',)
    date_hierarchy = 'date_debut'

    @admin.display(description="Durée")
    def duree_affichee(self, obj):
        return obj.duree_formatee()

    @admin.display(description="Coût estimé (€)")
    def cout_affiche(self, obj):
        return f"{obj.cout_estime()} €"