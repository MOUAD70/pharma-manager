from rest_framework import serializers
from .models import Vente, LigneVente


class LigneVenteSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour une ligne de vente.

    Champs supplémentaires:
        medicament_nom (str): Nom du médicament au moment de l'affichage.
        sous_total (Decimal): Calculé automatiquement, lecture seule.

    Note: prix_unitaire est renseigné automatiquement depuis le prix de vente
    du médicament si non fourni explicitement.
    """

    medicament_nom = serializers.CharField(
        source='medicament.nom',
        read_only=True,
        label='Nom du médicament'
    )

    prix_unitaire = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
        label='Prix unitaire (snapshot)'
    )

    class Meta:
        model = LigneVente
        fields = ['id', 'medicament', 'medicament_nom', 'quantite', 'prix_unitaire', 'sous_total']
        read_only_fields = ['sous_total']


class VenteSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle Vente.

    Champs supplémentaires:
        lignes (list): Liste imbriquée des LigneVente associées.
        statut_display (str): Libellé humain du statut.

    Comportement en écriture:
        - Les lignes sont créées en même temps que la vente (création imbriquée).
        - Le prix_unitaire est automatiquement snapshotté depuis medicament.prix_vente
          si non fourni dans la requête.
        - Le total_ttc est recalculé après la création/mise à jour des lignes.
        - Le stock de chaque médicament est décrémenté à la création.
    """

    lignes = LigneVenteSerializer(many=True, label='Lignes de vente')
    statut_display = serializers.CharField(
        source='get_statut_display',
        read_only=True,
        label='Statut (libellé)'
    )

    class Meta:
        model = Vente
        fields = [
            'id', 'reference', 'date_vente', 'total_ttc',
            'statut', 'statut_display', 'notes', 'date_creation', 'lignes'
        ]
        read_only_fields = ['reference', 'total_ttc', 'date_creation']

    def validate_lignes(self, lignes):
        """Vérifie qu'au moins une ligne est fournie."""
        if not lignes:
            raise serializers.ValidationError("Une vente doit contenir au moins une ligne.")
        return lignes

    def validate(self, attrs):
        """Vérifie le stock disponible pour chaque médicament."""
        lignes = attrs.get('lignes', [])
        for ligne in lignes:
            medicament = ligne['medicament']
            quantite = ligne['quantite']
            if medicament.stock_actuel < quantite:
                raise serializers.ValidationError(
                    f"Stock insuffisant pour '{medicament.nom}' : "
                    f"disponible={medicament.stock_actuel}, demandé={quantite}."
                )
        return attrs

    def create(self, validated_data):
        """
        Crée la vente et ses lignes, déduit le stock, calcule le total.
        Le prix_unitaire est snapshotté depuis medicament.prix_vente si absent.
        """
        lignes_data = validated_data.pop('lignes')
        vente = Vente.objects.create(**validated_data)

        for ligne_data in lignes_data:
            medicament = ligne_data['medicament']
            
            if 'prix_unitaire' not in ligne_data or ligne_data['prix_unitaire'] is None:
                ligne_data['prix_unitaire'] = medicament.prix_vente

            LigneVente.objects.create(vente=vente, **ligne_data)

            medicament.stock_actuel -= ligne_data['quantite']
            medicament.save(update_fields=['stock_actuel'])

        vente.recalculer_total()
        return vente