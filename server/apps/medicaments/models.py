from django.db import models

class Medicament(models.Model):
    """
    Représente un médicament dans l'inventaire de la pharmacie.

    Attributs:
        nom (str): Nom commercial du médicament.
        dci (str): Dénomination Commune Internationale.
        categorie (FK): Catégorie du médicament (ex: antibiotique, analgésique...).
        forme (str): Forme galénique (comprimé, sirop, injection...).
        dosage (str): Dosage du médicament (ex: 500mg, 250mg/5ml).
        prix_achat (Decimal): Prix d'achat unitaire.
        prix_vente (Decimal): Prix de vente public.
        stock_actuel (int): Quantité disponible en stock.
        stock_minimum (int): Seuil déclenchant une alerte de réapprovisionnement.
        date_expiration (date): Date de péremption du médicament.
        ordonnance_requise (bool): True si le médicament nécessite une ordonnance.
        date_creation (datetime): Horodatage automatique de création.
        est_actif (bool): Soft delete. False = médicament archivé.
    """

    nom = models.CharField(max_length=200, verbose_name='Nom commercial')
    dci = models.CharField(max_length=200, verbose_name='DCI', blank=True)
    categorie = models.ForeignKey(
        'categories.Categorie',
        on_delete=models.PROTECT,
        related_name='medicaments',
        verbose_name='Catégorie'
    )
    forme = models.CharField(max_length=100, verbose_name='Forme galénique')
    dosage = models.CharField(max_length=100, verbose_name='Dosage')
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix d'achat")
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Prix de vente')
    stock_actuel = models.PositiveIntegerField(default=0, verbose_name='Stock actuel')
    stock_minimum = models.PositiveIntegerField(default=10, verbose_name='Stock minimum')
    date_expiration = models.DateField(verbose_name='Date d\'expiration')
    ordonnance_requise = models.BooleanField(default=False, verbose_name='Ordonnance requise')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    est_actif = models.BooleanField(default=True, verbose_name='Actif')

    class Meta:
        verbose_name = 'Médicament'
        verbose_name_plural = 'Médicaments'
        ordering = ['nom']

    def __str__(self):
        return f'{self.nom} ({self.dosage})'

    @property
    def est_en_alerte(self):
        """Retourne True si le stock est inférieur ou égal au seuil minimum."""
        return self.stock_actuel <= self.stock_minimum