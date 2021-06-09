from django.contrib import admin
from django.urls import path

from functools import update_wrapper

from .forms import (
    BatchAddInstitutionForm,
    BatchAddInstitutionsFormPreview,
    InstitutionForm,
)
from .models import Institution


class InstitutionAdmin(admin.ModelAdmin):
    change_list_template = "django_esidoc/admin/change_list.html"

    raw_id_fields = ("user",)
    list_display = ("institution_name", "user", "uai", "ends_at")
    list_select_related = ("user",)
    ordering = ("institution_name",)
    search_fields = ("institution_name", "user__email", "uai")
    form = InstitutionForm

    def get_urls(self):

        urls = super().get_urls()

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            return update_wrapper(wrapper, view)

        custom_urls = [
            path(
                "batch_add/",
                wrap(BatchAddInstitutionsFormPreview(BatchAddInstitutionForm)),
                name="add_institutions",
            )
        ]

        return custom_urls + urls


admin.site.register(Institution, InstitutionAdmin)
