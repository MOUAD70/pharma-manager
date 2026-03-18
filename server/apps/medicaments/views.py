from django.db.models import F
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Medicament
from .serializers import MedicamentSerializer


class MedicamentViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des médicaments.

    Actions disponibles:
        list: Retourne la liste des médicaments actifs avec filtres et recherche.
        create: Ajoute un nouveau médicament.
        retrieve: Retourne le détail d'un médicament.
        update: Modifie un médicament existant.
        partial_update: Modifie partiellement un médicament existant.
        destroy: Soft delete — désactive le médicament.
        stock_alertes: Retourne les médicaments dont le stock est en alerte.
    """

    serializer_class = MedicamentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categorie', 'forme', 'ordonnance_requise', 'est_actif']
    search_fields = ['nom', 'dci', 'dosage']
    ordering_fields = ['nom', 'prix_vente', 'stock_actuel', 'date_expiration']

    def get_queryset(self):
        """Retourne uniquement les médicaments actifs."""
        return Medicament.objects.filter(est_actif=True)

    def perform_destroy(self, instance):
        """Soft delete — désactive le médicament au lieu de le supprimer."""
        instance.est_actif = False
        instance.save()

    @action(detail=False, methods=['get'], url_path='alertes')
    def stock_alertes(self, request):
        """Retourne les médicaments dont le stock est inférieur ou égal au seuil minimum."""
        alertes = Medicament.objects.filter(
            est_actif=True,
            stock_actuel__lte=F('stock_minimum')
        )
        serializer = self.get_serializer(alertes, many=True)
        return Response(serializer.data)