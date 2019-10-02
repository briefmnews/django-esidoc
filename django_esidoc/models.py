# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()


class Institution(models.Model):

    ENVIRONNEMENTS_NUMERIQUES_DE_TRAVAIL = [
        ("ESIDOC", "Esidoc"),
        ("HDF", "Hauts-de-France"),
        ("GAR", "GAR"),
    ]

    uai = models.CharField(
        "Unité Administrative Immatriculée", max_length=8, unique=True
    )
    institution_name = models.CharField("Nom de l'institution", max_length=255)
    ends_at = models.DateField("Date de fin d'abonnement", null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ent = models.CharField(
        "Environnements Numériques de Travail",
        choices=ENVIRONNEMENTS_NUMERIQUES_DE_TRAVAIL,
        default="ESIDOC",
        max_length=6,
    )

    def save(self, *args, **kwargs):
        self.uai = self.uai.upper()
        super(Institution, self).save(*args, **kwargs)
