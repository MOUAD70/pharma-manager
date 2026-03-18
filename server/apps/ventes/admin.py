from django.contrib import admin
from .models import Vente, LigneVente


class LigneVenteInline(admin.TabularInline):
    model = LigneVente
    extra = 1
    readonly_fields = ['sous_total']


@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    """Interface d'administration pour le modèle Vente."""

    list_display = ['reference', 'date_vente', 'total_ttc', 'statut', 'date_creation']
    list_filter = ['statut', 'date_vente']
    search_fields = ['reference', 'notes']
    readonly_fields = ['reference', 'total_ttc', 'date_creation']
    inlines = [LigneVenteInline]