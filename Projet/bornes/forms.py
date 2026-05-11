from django import forms
from .models import Borne, SessionCharge
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class SessionChargeForm(forms.ModelForm):
    class Meta:
        model  = SessionCharge
        fields = ['borne', 'date_debut', 'duree_minutes', 'energie_kwh']
        widgets = {
            'date_debut': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M'
            ),
            'borne': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'duree_minutes': forms.NumberInput(
                attrs={'class': 'form-control', 'min': 1}
            ),
            'energie_kwh': forms.NumberInput(
                attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['borne'].queryset = Borne.objects.all().order_by('identifiant')
        self.fields['borne'].empty_label = "— Sélectionner une borne —"
        if self.instance and self.instance.pk:
            self.initial['date_debut'] = self.instance.date_debut.strftime('%Y-%m-%dT%H:%M')


class BorneStatusForm(forms.ModelForm):
    class Meta:
        model = Borne
        fields = ['statut']
        widgets = {
            'statut': forms.Select(attrs={'class': 'form-select'})
        }