from django.contrib import admin

from .gar import delete_gar_subscription
from .forms import InstitutionForm
from .models import Institution


class InstitutionAdmin(admin.ModelAdmin):
    raw_id_fields = ("user",)
    list_display = ("institution_name", "ent", "user", "uai", "ends_at")
    list_select_related = ("user",)
    ordering = ("institution_name",)
    search_fields = ("institution_name", "user__email", "uai", "ent")
    form = InstitutionForm

    def delete_model(self, request, obj):
        if obj.ent == "GAR":
            delete_gar_subscription(obj.uai)
        super().delete_model(request, obj)


admin.site.register(Institution, InstitutionAdmin)
