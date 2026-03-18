import uuid
from django.db import models
from django.utils import timezone


def generer_reference():
    """Génère une référence unique au format VNT-YYYY-XXXX."""
    annee = timezone.now().year
    uid = uuid.uuid4().hex[:4].upper()
    return f'VNT-{annee}-{uid}'


class Vente(models.Model):
    """
    Représente une transaction de vente dans la pharmacie.

    Attributs:
        reference (str): Code unique auto-généré (ex: VNT-2024-0001).
        date_vente (datetime): Date et heure de la transaction.
        total_ttc (Decimal): Montant total calculé automatiquement.
        statut (str): État de la vente — En cours / Complétée / Annulée.
        notes (str): Remarques optionnelles.
        date_creation (datetime): Horodatage automatique de création.
    """

    class Statut(models.TextChoices):
        EN_COURS = 'en_cours', 'En cours'
        COMPLETEE = 'completee', 'Complétée'
        ANNULEE = 'annulee', 'Annulée'

    reference = models.CharField(
        max_length=20,
        unique=True,
        default=generer_reference,
        verbose_name='Référence'
    )
    date_vente = models.DateTimeField(
        default=timezone.now,
        verbose_name='Date de vente'
    )
    total_ttc = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Total TTC'
    )
    statut = models.CharField(
        max_length=20,
        choices=Statut.choices,
        default=Statut.EN_COURS,
        verbose_name='Statut'
    )
    notes = models.TextField(blank=True, verbose_name='Notes')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')

    class Meta:
        verbose_name = 'Vente'
        verbose_name_plural = 'Ventes'
        ordering = ['-date_vente']

    def __str__(self):
        return f'{self.reference} — {self.get_statut_display()}'

    def recalculer_total(self):
        """Recalcule et sauvegarde le total TTC depuis les lignes de vente."""
        total = sum(ligne.sous_total for ligne in self.lignes.all())
        self.total_ttc = total
        self.save(update_fields=['total_ttc'])


class LigneVente(models.Model):
    """
    Représente un article dans une vente (ligne de commande).

    Note métier : prix_unitaire est un snapshot du prix au moment de la vente.
    Il ne doit jamais être une FK vers le médicament — les prix peuvent évoluer.

    Attributs:
        vente (FK): La vente parente.
        medicament (FK): Le médicament vendu.
        quantite (int): Quantité vendue.
        prix_unitaire (Decimal): Prix au moment de la vente (snapshot).
        sous_total (Decimal): Calculé automatiquement : quantité × prix_unitaire.
    """

    vente = models.ForeignKey(
        Vente,
        on_delete=models.CASCADE,
        related_name='lignes',
        verbose_name='Vente'
    )
    medicament = models.ForeignKey(
        'medicaments.Medicament',
        on_delete=models.PROTECT,
        related_name='lignes_vente',
        verbose_name='Médicament'
    )
    quantite = models.PositiveIntegerField(verbose_name='Quantité')
    prix_unitaire = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Prix unitaire (snapshot)'
    )
    sous_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Sous-total'
    )

    class Meta:
        verbose_name = 'Ligne de vente'
        verbose_name_plural = 'Lignes de vente'

    def __str__(self):
        return f'{self.medicament.nom} × {self.quantite} ({self.vente.reference})'

    def save(self, *args, **kwargs):
        """Calcule automatiquement le sous_total avant la sauvegarde."""
        self.sous_total = self.quantite * self.prix_unitaire
        super().save(*args, **kwargs)