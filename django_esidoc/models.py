from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()


class Institution(models.Model):

    ENVIRONNEMENTS_NUMERIQUES_DE_TRAVAIL = [
        ("ESIDOC", "Esidoc"),
        ("HDF", "Hauts-de-France"),
        ("OCCITANIE", "Occitanie"),
        ("OCCITANIEAGR", "Occitanie lycée agricole"),
        ("CORRELYCE", "Corrélyce"),
        ("GMINVENT", "GMInvent"),
    ]

    uai = models.CharField(
        "Unité Administrative Immatriculée", max_length=14, unique=True
    )
    institution_name = models.CharField("Nom de l'institution", max_length=255)
    ends_at = models.DateField("Date de fin d'abonnement", null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ent = models.CharField(
        "Environnements Numériques de Travail",
        choices=ENVIRONNEMENTS_NUMERIQUES_DE_TRAVAIL,
        default="ESIDOC",
        max_length=12,
    )

    def __str__(self):
        return "{} ({})".format(self.institution_name, self.uai)
