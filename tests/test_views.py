# -*- coding: utf-8 -*-
import pytest

from django.urls import reverse

from django_esidoc.views import LogoutRedirectView

pytestmark = pytest.mark.django_db


class TestLogoutRedirectView(object):

    @staticmethod
    def test_url_redirect_works(request_builder):
        """
        The logout view should redirect to esidoc a 'service' query string
        """
        # GIVEN
        request = request_builder.build(reverse('esidoc_logout'))

        # WHEN
        response = LogoutRedirectView.as_view()(request)

        # THEN
        assert response.status_code == 302
        assert '?service=' in response.url
