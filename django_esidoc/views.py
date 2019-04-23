# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import RedirectView

from .utils import (
    get_cas_client,
    get_redirect_url,
)


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
        url = '{}?service={}'.format(base_url, redirect_url)

        return url
