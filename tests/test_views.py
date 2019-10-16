# -*- coding: utf-8 -*-
import pytest

from django.urls import reverse

from django_esidoc.views import InstitutionViewSet, LogoutRedirectView

pytestmark = pytest.mark.django_db


class TestLogoutRedirectView(object):
    @staticmethod
    def test_url_redirect_works(request_builder):
        """
        The logout view should redirect to esidoc a 'service' query string
        """
        # GIVEN
        request = request_builder.get(reverse("esidoc_logout"))

        # WHEN
        response = LogoutRedirectView.as_view()(request)

        # THEN
        assert response.status_code == 302
        assert "?service=" in response.url


class TestInstitutionViewSet(object):
    def test_authentication_works(self, request_builder):
        # GIVEN
        url = "{}?token={}".format(reverse("esidoc_institutions"), "my-secret-token")
        request = request_builder.get(url)

        # WHEN
        response = InstitutionViewSet.as_view({"get": "list"})(request)

        # THEN
        assert response.status_code == 200

    def test_authenticate_with_wrong_token(self, request_builder):
        # GIVEN
        url = "{}?token={}".format(reverse("esidoc_institutions"), "wrong-token")
        request = request_builder.get(url)

        # WHEN
        response = InstitutionViewSet.as_view({"get": "list"})(request)
        response.render()

        # THEN
        assert response.status_code == 403
        assert b"The token value is wrong" in response.content

    def test_authenticate_without_token(self, request_builder):
        # GIVEN
        request = request_builder.get(reverse("esidoc_institutions"))

        # WHEN
        response = InstitutionViewSet.as_view({"get": "list"})(request)
        response.render()

        # THEN
        assert response.status_code == 403
        assert b"Authentication credentials were not provided" in response.content
