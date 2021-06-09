import datetime
import re

from datetime import datetime
from formtools.preview import FormPreview

from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.forms import ModelForm, ValidationError
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from .models import Institution

User = get_user_model()


class InstitutionForm(ModelForm):
    class Meta:
        model = Institution
        fields = ("uai", "institution_name", "ends_at", "user")

    def clean_uai(self):
        return self.cleaned_data.get("uai").upper()


class BatchAddInstitutionForm(forms.Form):
    institutions_data = forms.CharField(
        widget=forms.Textarea,
        required=True,
        help_text=_(
            "Copy/paste the csv with the following format: email "
            "(mandatory), uai (mandatory), intitution name (mandatory)."
        ),
    )

    def clean_institutions_data(self):
        institutions_data = self._get_institution_fields(
            self.cleaned_data["institutions_data"]
        )

        return institutions_data

    @staticmethod
    def _get_institution_fields(institutions_data):
        sep = re.compile(r"[,\t]")
        ret = []

        for data in institutions_data.split("\n"):
            fields = sep.split(data)
            try:
                email = fields[0].lower().strip()
            except IndexError:
                raise ValidationError(_("Email is madatory"))
            try:
                uai = fields[1].upper().strip()
            except IndexError:
                raise ValidationError(_("Uai number is madatory"))
            try:
                institution_name = fields[2].strip()
            except IndexError:
                raise ValidationError(_("Institution name is madatory"))

            ret.append((email, uai, institution_name))

        return ret


class BatchAddInstitutionsFormPreview(FormPreview):
    preview_template = "django_esidoc/admin/preview.html"
    form_template = "django_esidoc/admin/form.html"

    def process_preview(self, request, form, context):
        emails = [email for email, _, _, _ in form.cleaned_data["institutions_data"]]
        existing_users = User.objects.filter(email__in=emails)
        context["users_found_count"] = existing_users.count()
        context["users_not_found_count"] = len(emails) - existing_users.count()
        context["users_not_found"] = set(emails) - set(
            existing_users.values_list("email", flat=True)
        )

        return context

    def done(self, request, cleaned_data):
        institutions_data = cleaned_data["institutions_data"]

        for institution_detail in institutions_data:
            try:
                user = User.objects.get(email=institution_detail[0])
            except User.DoesNotExist:
                continue

            Institution.objects.create(
                user=user,
                uai=institution_detail[1],
                institution_name=institution_detail[2],
                ends_at=datetime.now(),
            )

        messages.info(request, _("La commande a bien été prise en compte."))

        return redirect(reverse("admin:django_esidoc_institution_changelist"))
