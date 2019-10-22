import requests

from datetime import datetime

from django.conf import settings
from django.forms import ModelForm, ValidationError

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
           <typeAffectation>ETABL</typeAffectation>
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
