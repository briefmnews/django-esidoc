# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect

from django.conf import settings
from django.contrib.auth import login, authenticate

from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError

from .utils import get_cas_client
from .models import Institution

ESIDOC_INACTIVE_USER_REDIRECT = getattr(settings, "ESIDOC_INACTIVE_USER_REDIRECT", "/")


class CASMiddleware(object):
    """
    Middleware that allows CAS authentication with different kind of ENT
    (Esidoc, ENT Hauts-de-France, ...)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        uai_number = request.GET.get("sso_id", "")
        cas_ticket = request.GET.get("ticket", "")

        if cas_ticket:

            uai_numbers = self.validate_ticket(request, cas_ticket)

            user = authenticate(uai_numbers=uai_numbers)
            if user:
                login(request, user)
            else:
                return HttpResponseRedirect(ESIDOC_INACTIVE_USER_REDIRECT)

        elif uai_number:
            uai_number = uai_number.upper()

            if uai_number == "GAR":
                request.session["uai_number"] = None
                request.session["ent"] = "GAR"
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
        tree = ElementTree.fromstring(response)
        ns = {"cas": "http://www.yale.edu/tp/cas"}

        try:
            auth_success_element = tree.find("cas:authenticationSuccess", ns)

            if request.session.get("ent") == "ESIDOC":
                uai_element = "cas:ENTStructureUAI"
            else:
                uai_element = "cas:ENTPersonStructRattachRNE"

            uai_numbers = [
                uai.text for uai in auth_success_element.findall(uai_element, ns)
            ]
            return uai_numbers

        except (AttributeError, ParseError):
            return None
