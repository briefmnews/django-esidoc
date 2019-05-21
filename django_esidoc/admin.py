# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Institution


class InstitutionAdmin(admin.ModelAdmin):
    raw_id_fields = ("user",)
    list_display = ("institution_name", "user", "uai")
    list_select_related = ("user",)
    ordering = ("institution_name",)
    search_fields = ("institution_name", "user__email", "uai")


admin.site.register(Institution, InstitutionAdmin)
