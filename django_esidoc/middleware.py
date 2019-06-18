# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect

from django.conf import settings
from django.contrib.auth import login, authenticate

from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError

from .utils import get_cas_client


ESIDOC_DEFAULT_REDIRECT = getattr(settings, "ESIDOC_DEFAULT_REDIRECT", "/")
ESIDOC_INACTIVE_USER_REDIRECT = getattr(settings, "ESIDOC_INACTIVE_USER_REDIRECT", "/")


class CASMiddleware(object):
    """Middleware that allows CAS authentication with e-sidoc"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        uai_number = request.GET.get("sso_id", "")
        cas_ticket = request.GET.get("ticket", "")

        if uai_number:

            request.session["uai_number"] = uai_number.upper()

            url = self.get_cas_login_url(request)
            return HttpResponseRedirect(url)

        elif cas_ticket:

            uai_number = self.validate_ticket(request, cas_ticket)

            if uai_number == request.session.get("uai_number"):
                user = authenticate(uai_number=uai_number)
                if user:
                    login(request, user)
                else:
                    return HttpResponseRedirect(ESIDOC_INACTIVE_USER_REDIRECT)

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
            uai_element = auth_success_element.find("cas:ENTStructureUAI", ns)
            return uai_element.text
        except (AttributeError, ParseError):
            return None
