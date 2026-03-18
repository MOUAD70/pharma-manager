from rest_framework import serializers

from .models import Categorie


class CategorieSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le modèle Categorie."""

    class Meta:
        model = Categorie
        fields = '__all__'
        read_only_fields = ['date_creation']
