from django.contrib import admin

from .models import Categorie


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    """Interface d'administration pour le modèle Categorie."""

    list_display = ['nom', 'est_actif']
    list_filter = ['est_actif']
    search_fields = ['nom']
    readonly_fields = ['date_creation']
