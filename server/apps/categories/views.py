from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Categorie
from .serializers import CategorieSerializer


class CategorieViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des catégories de médicaments."""

    serializer_class = CategorieSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['est_actif']
    search_fields = ['nom']
    ordering_fields = ['nom']

    def get_queryset(self):
        """Retourne uniquement les catégories actives."""
        return Categorie.objects.filter(est_actif=True)

    def perform_destroy(self, instance):
        """Soft delete — désactive la catégorie au lieu de la supprimer."""
        instance.est_actif = False
        instance.save(update_fields=['est_actif'])
