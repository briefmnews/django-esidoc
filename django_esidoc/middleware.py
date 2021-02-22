from django.http import HttpResponseRedirect

from django.conf import settings
from django.contrib.auth import login, authenticate

from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError

from .backends import CASBackend
from .utils import get_cas_client
from .models import Institution

ESIDOC_INACTIVE_USER_REDIRECT = getattr(settings, "ESIDOC_INACTIVE_USER_REDIRECT", "/")
ENT_QUERY_STRING_TRIGGER = getattr(settings, "ENT_QUERY_STRING_TRIGGER", "sso_id")


class CASMiddleware:
    """
    Middleware that allows CAS authentication with different kind of ENT
    (Esidoc, ENT Hauts-de-France, ...)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        uai_number = request.GET.get(ENT_QUERY_STRING_TRIGGER) or request.GET.get(
            "uai", ""
        )
        cas_ticket = request.GET.get("ticket", "")
        pf = request.GET.get("pf", "")

        if cas_ticket and not pf:
            uai_numbers = self.validate_ticket(request, cas_ticket)

            user = CASBackend.authenticate(request, uai_numbers=uai_numbers)
            if user:
                login(request, user, backend="django_esidoc.backends.CASBackend")
                request.esidoc_user = True
            else:
                return HttpResponseRedirect(ESIDOC_INACTIVE_USER_REDIRECT)

        elif uai_number:
            uai_number = uai_number.upper()

            if uai_number in ["OCCITANIE", "OCCITANIEAGR"]:
                request.session["uai_number"] = None
                request.session["ent"] = uai_number
            else:
                try:
                    ent = Institution.objects.get(uai=uai_number).ent
                except Institution.DoesNotExist:
                    return HttpResponseRedirect(ESIDOC_INACTIVE_USER_REDIRECT)

                request.session["uai_number"] = uai_number
                request.session["ent"] = ent

            url = self.get_cas_login_url(request)
            return HttpResponseRedirect(url)

        response = self.get_response(request)

        return response

    @staticmethod
    def get_cas_login_url(request):
        """Returns the CAS login url"""

        client = get_cas_client(request)

        return client.get_login_url()

    @staticmethod
    def validate_ticket(request, cas_ticket):
        """
        Validate the CAS ticket. Ticket lifetime is around 5 seconds.
        Returns the uai number if the user has access, None otherwise
        """

        client = get_cas_client(request)
        response = client.get_verification_response(cas_ticket)

        try:
            tree = ElementTree.fromstring(response)
            ns = {"cas": "http://www.yale.edu/tp/cas"}
            auth_success_element = tree.find("cas:authenticationSuccess", ns)
            ent = request.session.get("ent", "")

            if ent == "ESIDOC":
                uai_element = "cas:ENTStructureUAI"
            elif ent in ["OCCITANIE", "OCCITANIEAGR"]:
                uai_element = "cas:rneCourant"
            elif ent == "CORRELYCE":
                auth_success_element = auth_success_element.find("cas:attributes", ns)
                uai_element = "cas:ENTPersonStructRattachUAI"
            elif ent == "HDF":
                uai_element = "cas:ENTPersonStructRattachRNE"
            else:
                return []

            uai_numbers = [
                uai.text.upper()
                for uai in auth_success_element.findall(uai_element, ns)
            ]
            return uai_numbers

        except (AttributeError, ParseError):
            return []
