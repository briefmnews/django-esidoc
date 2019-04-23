# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()


class Institution(models.Model):
    uai = models.CharField('Unité Administrative Immatriculée', max_length=8)
    institution_name = models.CharField('Nom de l\'institution', max_length=255)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )

    def save(self, *args, **kwargs):
        self.uai = self.uai.upper()
        super(Institution, self).save(*args, **kwargs)
