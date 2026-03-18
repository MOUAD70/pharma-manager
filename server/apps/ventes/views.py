from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Vente, LigneVente
from .serializers import VenteSerializer


class VenteViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des ventes.

    Actions disponibles:
        list:           Retourne l'historique des ventes avec filtres par date et statut.
        create:         Crée une nouvelle vente avec ses lignes (stock déduit automatiquement).
        retrieve:       Retourne le détail d'une vente avec toutes ses lignes.
        update:         Mise à jour complète d'une vente (statut, notes).
        partial_update: Mise à jour partielle d'une vente.
        destroy:        Désactivé — utiliser l'action 'annuler' à la place.
        annuler:        Annule une vente et réintègre les quantités en stock (soft delete).
    """

    serializer_class = VenteSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['statut']
    ordering_fields = ['date_vente', 'total_ttc', 'reference']
    ordering = ['-date_vente']

    def get_queryset(self):
        """
        Retourne les ventes avec filtrage optionnel par plage de dates.
        Paramètres query string supportés: date_debut, date_fin (format YYYY-MM-DD).
        """
        queryset = Vente.objects.prefetch_related('lignes__medicament')

        date_debut = self.request.query_params.get('date_debut')
        date_fin = self.request.query_params.get('date_fin')

        if date_debut:
            queryset = queryset.filter(date_vente__date__gte=date_debut)
        if date_fin:
            queryset = queryset.filter(date_vente__date__lte=date_fin)

        return queryset

    def destroy(self, request, *args, **kwargs):
        """Bloque la suppression directe — passer par l'action 'annuler'."""
        return Response(
            {'detail': "La suppression directe n'est pas autorisée. Utilisez l'action /annuler/."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @action(detail=True, methods=['post'], url_path='annuler')
    def annuler(self, request, pk=None):
        """
        Annule une vente et réintègre les quantités vendues dans le stock (soft delete).
        Une vente déjà annulée ne peut pas être annulée de nouveau.
        """
        vente = self.get_object()

        if vente.statut == Vente.Statut.ANNULEE:
            return Response(
                {'detail': 'Cette vente est déjà annulée.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        for ligne in vente.lignes.select_related('medicament'):
            medicament = ligne.medicament
            medicament.stock_actuel += ligne.quantite
            medicament.save(update_fields=['stock_actuel'])

        vente.statut = Vente.Statut.ANNULEE
        vente.save(update_fields=['statut'])

        serializer = self.get_serializer(vente)
        return Response(serializer.data, status=status.HTTP_200_OK)