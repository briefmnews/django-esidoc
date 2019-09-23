# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import RedirectView

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .authentication import QueryStringAuthentication
from .models import Institution
from .serializers import InstitutionSerializer
from .utils import get_cas_client, get_redirect_url


class LogoutRedirectView(RedirectView):
    def get_redirect_url(self):
        url = self.get_cas_logout_url(self.request)
        return url

    @staticmethod
    def get_cas_logout_url(request):
        """
        Returns the CAS logout url.
        The 'service' query string redirect the user after logout
        """

        client = get_cas_client(request)
        base_url = client.get_logout_url()
        redirect_url = get_redirect_url(request)
        url = "{}?service={}".format(base_url, redirect_url)

        return url


class InstitutionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Institution.objects.filter(ent="ESIDOC")
    serializer_class = InstitutionSerializer
    authentication_classes = (QueryStringAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = None
