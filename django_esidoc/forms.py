import datetime
import re
import requests

from datetime import datetime
from formtools.preview import FormPreview

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.forms import ModelForm, ValidationError
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from .gar import (
    delete_gar_subscription,
    get_gar_certificate,
    get_gar_headers,
    get_gar_request_url,
    get_gar_subscription_id,
)
from .models import Institution

ENT_GAR_DISTRIBUTOR_ID = getattr(settings, "ENT_GAR_DISTRIBUTOR_ID", "")
ENT_GAR_RESOURCES_ID = getattr(settings, "ENT_GAR_RESOURCES_ID", "")
ENT_GAR_ORGANIZATION_NAME = getattr(settings, "ENT_GAR_ORGANIZATION_NAME", "")
User = get_user_model()


class InstitutionForm(ModelForm):
    class Meta:
        model = Institution
        fields = ("uai", "institution_name", "ends_at", "user", "ent")

    def clean_uai(self):
        return self.cleaned_data.get("uai").upper()

    def clean_ent(self):
        ent = self.cleaned_data.get("ent")
        if ent == "GAR":
            self._create_or_update_gar_subscription()
        elif (self.initial.get("ent") == "GAR") and ("ent" in self.changed_data):
            delete_gar_subscription(self.clean_uai())

        return ent

    def _create_or_update_gar_subscription(self):
        """
        A GAR subscription needs to be created or
        updated when an action occurred in the Back Office.
        Creating a subscription is done via PUT method.
        Updating a subscription is done via POST method.
        """

        if not self.initial or ("ent" in self.changed_data):
            response = self._get_response_from_gar(http_method="PUT")
            if response.status_code not in [201, 200]:
                raise ValidationError(response.text)
        else:
            response = self._get_response_from_gar(http_method="POST")
            if response.status_code != 200:
                raise ValidationError(response.text)

    def _get_response_from_gar(self, http_method):
        url = get_gar_request_url(self.clean_uai())
        cert = get_gar_certificate()
        headers = get_gar_headers()
        response = requests.request(
            http_method,
            url,
            data=self._get_gar_data_to_send(http_method=http_method),
            cert=cert,
            headers=headers,
        )

        if response.status_code == 409 and "existe deja" in response.text:
            response = self._get_response_from_gar(http_method="POST")

        return response

    def _get_gar_data_to_send(self, http_method=None):
        """
        This is the data that needs to be sent when creating a subscription (PUT)
        or when updating a subscription (POST).
        When updating a subscription, the uaiEtab child should be removed.
        """
        uai = self.clean_uai()
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <abonnement xmlns="http://www.atosworldline.com/wsabonnement/v1.0/">
           <idAbonnement>{subscription_id}</idAbonnement>
           <idDistributeurCom>{distributor_id}</idDistributeurCom>
           <idRessource>{resources_id}</idRessource>
           <typeIdRessource>ark</typeIdRessource>
           <libelleRessource>{organization_name}</libelleRessource>
           <debutValidite>{start_date}</debutValidite>
           <finValidite>{end_date}T00:00:00</finValidite>
           <uaiEtab>{uai}</uaiEtab>
           <categorieAffectation>transferable</categorieAffectation>
           <typeAffectation>INDIV</typeAffectation>
           <nbLicenceGlobale>ILLIMITE</nbLicenceGlobale>
           <publicCible>ELEVE</publicCible>
           <publicCible>ENSEIGNANT</publicCible>
           <publicCible>DOCUMENTALISTE</publicCible>
        </abonnement>""".format(
            subscription_id=get_gar_subscription_id(uai),
            distributor_id=ENT_GAR_DISTRIBUTOR_ID,
            resources_id=ENT_GAR_RESOURCES_ID,
            organization_name=ENT_GAR_ORGANIZATION_NAME,
            start_date=datetime.now().isoformat(),
            end_date=self.cleaned_data.get("ends_at"),
            uai=uai,
        )

        if http_method == "POST":
            xml = xml.replace("<uaiEtab>{uai}</uaiEtab>".format(uai=uai), "")

        return xml


class BatchAddInstitutionForm(forms.Form):
    institutions_data = forms.CharField(
        widget=forms.Textarea,
        required=True,
        help_text=_(
            "Copy/paste the csv with the following format: email "
            "(mandatory), uai (mandatory), ent (mandatory), intitution name (mandatory"
        ),
    )

    def clean_institutions_data(self):
        institutions_data = self._get_institution_fields(self.cleaned_data["institutions_data"])
        for institution_detail in institutions_data:
            ent = institution_detail[2]
            ent_choices = [val[0] for val in Institution.ENVIRONNEMENTS_NUMERIQUES_DE_TRAVAIL]
            if ent not in ent_choices:
                raise ValidationError(_('ENTs must take ine of the following values: {}'.format(ent_choices)))

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
                raise ValidationError(_('Email is madatory'))
            try:
                uai = fields[1].upper().strip()
            except IndexError:
                raise ValidationError(_('Uai number is madatory'))
            try:
                ent = fields[2].upper().strip()
            except IndexError:
                raise ValidationError(_('Ent is madatory'))
            try:
                institution_name = fields[3].strip()
            except IndexError:
                raise ValidationError(_('Institution name is madatory'))

            ret.append((email, uai, ent, institution_name))

        return ret


class BatchAddInstitutionsFormPreview(FormPreview):
    preview_template = "django_esidoc/admin/preview.html"
    form_template = "django_esidoc//admin/form.html"

    def process_preview(self, request, form, context):
        emails = [email for email, _, _, _ in form.cleaned_data["institutions_data"]]
        existing_users = User.objects.filter(email__in=emails)
        context["users_found_count"] = existing_users.count()
        context["users_not_found_count"] = len(emails) - existing_users.count()

        return context

    def done(self, request, cleaned_data):
        institutions_data = cleaned_data["institutions_data"]

        for institution_detail in institutions_data:
            try:
                user = User.objects.get(email=institution_detail[0])
            except User.DoesNotExist:
                continue

            Institution.objects.create(user=user, uai=institution_detail[1], ent=institution_detail[2], institution_name=institution_detail[3], ends_at=datetime.now())

        messages.info(
            request,
            (
                "La commande a bien été prise en compte."
            ),
        )

        return redirect(reverse("admin:django_esidoc_institution_changelist"))
