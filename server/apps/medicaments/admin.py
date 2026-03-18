from django.contrib import admin
from .models import Medicament


@admin.register(Medicament)
class MedicamentAdmin(admin.ModelAdmin):
    """
    Interface d'administration pour le modèle Medicament.
    """

    list_display = ['nom', 'dci', 'categorie', 'stock_actuel', 'stock_minimum', 'est_en_alerte', 'est_actif']
    list_filter = ['categorie', 'forme', 'ordonnance_requise', 'est_actif']
    search_fields = ['nom', 'dci']
    readonly_fields = ['date_creation']