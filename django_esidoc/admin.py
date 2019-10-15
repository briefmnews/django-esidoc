from django.contrib import admin

from .forms import InstitutionForm
from .models import Institution


class InstitutionAdmin(admin.ModelAdmin):
    raw_id_fields = ("user",)
    list_display = ("institution_name", "ent", "user", "uai", "ends_at")
    list_select_related = ("user",)
    ordering = ("institution_name",)
    search_fields = ("institution_name", "user__email", "uai", "ent")
    form = InstitutionForm


admin.site.register(Institution, InstitutionAdmin)
