import requests

from datetime import datetime

from django.conf import settings
from django.forms import ModelForm, ValidationError

from .models import Institution

ENT_GAR_SUBSCRIPTION_PREFIX = getattr(settings, "ENT_GAR_SUBSCRIPTION_PREFIX", "")
ENT_GAR_BASE_SUBSCRIPTION_URL = getattr(
    settings,
    "ENT_GAR_BASE_SUBSCRIPTION_URL",
    "https://abonnement.partenaire.test-gar.education.fr/",
)

ENT_GAR_CERTIFICATE_PATH = getattr(settings, "ENT_GAR_CERTIFICATE_PATH", "")
ENT_GAR_KEY_PATH = getattr(settings, "ENT_GAR_KEY_PATH", "")

ENT_GAR_DISTRIBUTOR_ID = getattr(settings, "ENT_GAR_DISTRIBUTOR_ID", "")
ENT_GAR_RESOURCES_ID = getattr(settings, "ENT_GAR_RESOURCES_ID", "")
ENT_GAR_ORGANIZATION_NAME = getattr(settings, "ENT_GAR_ORGANIZATION_NAME", "")


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
            self._delete_gar_subscription()

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

    def _delete_gar_subscription(self):
        url = self._get_gar_request_url()
        cert = self._get_gar_certificate()
        headers = self._get_gar_headers()
        response = requests.delete(url, cert=cert, headers=headers)
        if response.status_code != 204:
            raise ValidationError(response.text)

    def _get_response_from_gar(self, http_method):
        url = self._get_gar_request_url()
        cert = self._get_gar_certificate()
        headers = self._get_gar_headers()
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
           <typeAffectation>ETABL</typeAffectation>
           <nbLicenceGlobale>ILLIMITE</nbLicenceGlobale>
           <publicCible>ELEVE</publicCible>
           <publicCible>ENSEIGNANT</publicCible>
           <publicCible>DOCUMENTALISTE</publicCible>
        </abonnement>""".format(
            subscription_id=self._get_gar_subscription_id(uai),
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

    @staticmethod
    def _get_gar_subscription_id(uai):
        """
        The id of the subscription in the GAR.
        It needs to be unique even among all organizations
        """
        subscription_id = "{}{}".format(ENT_GAR_SUBSCRIPTION_PREFIX, uai)
        return subscription_id

    def _get_gar_request_url(self):
        base_url = ENT_GAR_BASE_SUBSCRIPTION_URL
        subscription_id = self._get_gar_subscription_id(self.clean_uai())
        url = "{}{}".format(base_url, subscription_id)
        return url

    @staticmethod
    def _get_gar_certificate():
        cert = (ENT_GAR_CERTIFICATE_PATH, ENT_GAR_KEY_PATH)
        return cert

    @staticmethod
    def _get_gar_headers():
        headers = {"Content-Type": "application/xml"}
        return headers
