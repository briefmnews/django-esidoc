import logging

from django.http import HttpResponseRedirect

from django.conf import settings
from django.contrib.auth import login, authenticate

from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError

from .utils import get_cas_client

logger = logging.getLogger(__name__)

ESIDOC_INACTIVE_USER_REDIRECT = getattr(settings, "ESIDOC_INACTIVE_USER_REDIRECT", "/")
ESIDOC_QUERY_STRING_TRIGGER = getattr(
    settings, "ESIDOC_QUERY_STRING_TRIGGER", "esidoc_sso_id"
)


class CASMiddleware:
    """
    Middleware that allows CAS authentication with different kind of ENT
    (Esidoc, ENT Hauts-de-France, ...)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        uai_number = request.GET.get(ESIDOC_QUERY_STRING_TRIGGER, None)
        cas_ticket = request.GET.get("ticket", "")
        redirect = request.GET.get("redirect", "")

        if cas_ticket and request.session.get("is_esidoc"):
            del request.session["is_esidoc"]
            uai_numbers = self.validate_ticket(request, cas_ticket)

            user = authenticate(request, esidoc_uai_numbers=uai_numbers)
            if user:
                login(request, user, backend="django_esidoc.backends.CASBackend")
                request.session["esidoc_user"] = True

                if redirect:
                    return HttpResponseRedirect(redirect)
            else:
                return HttpResponseRedirect(ESIDOC_INACTIVE_USER_REDIRECT)

        elif uai_number:
            request.session["uai_number"] = uai_number.upper()
            url = self.get_cas_login_url(request)
            request.session["is_esidoc"] = True
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

        logger.info(response)

        try:
            tree = ElementTree.fromstring(response)
            ns = {"cas": "http://www.yale.edu/tp/cas"}
            auth_success_element = tree.find("cas:authenticationSuccess", ns)

            uai_element = "cas:ENTStructureUAI"

            uai_numbers = [
                uai.text.upper()
                for uai in auth_success_element.findall(uai_element, ns)
            ]
            return uai_numbers

        except (AttributeError, ParseError):
            return []
