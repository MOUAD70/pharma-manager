from rest_framework import serializers
from .models import Medicament


class MedicamentSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle Medicament.

    Champs supplémentaires:
        est_en_alerte (bool): True si le stock est inférieur ou égal au seuil minimum.
        categorie_nom (str): Nom de la catégorie associée au médicament.
    """

    est_en_alerte = serializers.ReadOnlyField()
    categorie_nom = serializers.CharField(
        source='categorie.nom',
        read_only=True,
        label='Nom de la catégorie'
    )

    class Meta:
        model = Medicament
        fields = '__all__'