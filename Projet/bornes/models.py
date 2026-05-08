from django.db import models

# Create your models here.

class TypeConnecteur(models.Model):
    VITESSE_CHOICES = [
        ('standard', 'Standard'),
        ('rapide',   'Rapide'),
    ]

    nom = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nom du connecteur"
    )
    vitesse_charge = models.CharField(
        max_length=20,
        choices=VITESSE_CHOICES,
        default='standard',
        verbose_name="Vitesse de charge"
    )

    class Meta:
        verbose_name        = "Type de connecteur"
        verbose_name_plural = "Types de connecteurs"

    def __str__(self):
        return f"{self.nom} ({self.get_vitesse_charge_display()})"


class Borne(models.Model):
    STATUT_CHOICES = [
        ('libre',       'Libre'),
        ('occupee',     'Occupée'),
        ('maintenance', 'En maintenance'),
    ]

    identifiant      = models.CharField(max_length=30, unique=True, verbose_name="Identifiant")
    emplacement      = models.CharField(max_length=200, verbose_name="Emplacement / Adresse")
    ville            = models.CharField(max_length=100, verbose_name="Ville", default="")
    puissance_kw     = models.DecimalField(max_digits=6, decimal_places=1, verbose_name="Puissance (kW)")
    statut           = models.CharField(max_length=20, choices=STATUT_CHOICES, default='libre', verbose_name="Statut")
    type_connecteur  = models.ForeignKey(
        TypeConnecteur,
        on_delete=models.PROTECT,
        verbose_name="Type de connecteur",
        null=True, blank=True
    )
    date_installation = models.DateField(verbose_name="Date d'installation")

    class Meta:
        verbose_name        = "Borne de recharge"
        verbose_name_plural = "Bornes de recharge"
        ordering            = ['identifiant']

    def __str__(self):
        return f"{self.identifiant} — {self.ville} [{self.get_statut_display()}]"

    def badge_class(self):
        """Retourne la classe Bootstrap correspondant au statut."""
        mapping = {
            'libre':       'badge bg-primary',
            'occupee':     'badge bg-warning text-dark',
            'maintenance': 'badge bg-secondary',
        }
        return mapping.get(self.statut, 'badge bg-light')
    
class SessionCharge(models.Model):
    borne          = models.ForeignKey(
        Borne,
        on_delete=models.CASCADE,
        verbose_name="Borne"
    )
    date_debut     = models.DateTimeField(verbose_name="Date de début")
    duree_minutes  = models.PositiveIntegerField(verbose_name="Durée (minutes)")
    energie_kwh    = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Énergie délivrée (kWh)"
    )

    class Meta:
        verbose_name        = "Session de charge"
        verbose_name_plural = "Sessions de charge"
        ordering            = ['-date_debut']

    def __str__(self):
        return f"Session {self.borne.identifiant} — {self.date_debut.strftime('%d/%m/%Y %H:%M')}"

    def duree_formatee(self):
        """Convertit les minutes en format hh:mm."""
        heures  = self.duree_minutes // 60
        minutes = self.duree_minutes % 60
        return f"{heures}h{minutes:02d}"

    def cout_estime(self, tarif_kwh=0.20):
        """Coût estimé en euros selon le tarif au kWh."""
        return round(float(self.energie_kwh) * tarif_kwh, 2)