# -*- coding: utf-8 -*-
import pytest

from django_esidoc.middleware import CASMiddleware

pytestmark = pytest.mark.django_db


class TestCASMiddleware(object):
    @staticmethod
    def test_init():
        """Testing the __init__ method"""
        # WHEN
        cas_middleware = CASMiddleware("dump_response")

        # THEN
        assert cas_middleware.get_response == "dump_response"

    def test_no_uai_no_ticket(self, request_builder):
        """Testing the middleware if not a connection to esidoc"""
        # GIVEN
        cas_middleware = CASMiddleware(request_builder.build)

        # WHEN
        response = cas_middleware(request_builder.build())

        # THEN
        assert cas_middleware.get_response().path == "/"
        assert "sso_id" not in response.GET
        assert "ticket" not in response.GET

    @staticmethod
    def test_when_uai_number(user, request_builder):
        """Testing the __call__ method with uai_number in url"""
        # GIVEN
        uai_number = user.institution.uai
        query_params = "/?sso_id={}".format(uai_number)
        request = request_builder.build(query_params)
        cas_middleware = CASMiddleware(request)

        # WHEN
        response = cas_middleware(request)

        # THEN
        assert "https://{}-cas.esidoc.fr".format(uai_number) in response.url

    def test_when_cas_ticket_valid(
        self, mock_validate_valid_ticket, user, request_builder
    ):
        """
        Testing the __call__ method with valid cas_ticket in url and user
        has access (is_active is True)
        """
        # GIVEN
        uai_number = user.institution.uai
        cas_ticket = "this-is-a-ticket"
        query_params = "/?ticket={}".format(cas_ticket)
        request = request_builder.build(query_params)
        request.session["uai_number"] = uai_number
        cas_middleware = CASMiddleware(request)

        # WHEN
        try:
            cas_middleware(request)
        except:
            pass

        # THEN
        assert cas_middleware.validate_ticket.call_count == 1

    def test_when_cas_ticket_invalid(
        self, mock_validate_invalid_ticket, user, request_builder
    ):
        """
        Testing the __call__ method with cas_ticket in url and user
        has access (is_active is True)
        """
        # GIVEN
        uai_number = user.institution.uai
        cas_ticket = "this-is-a-ticket"
        query_params = "/?ticket={}".format(cas_ticket)
        request = request_builder.build(query_params)
        request.session["uai_number"] = uai_number
        cas_middleware = CASMiddleware(request)

        # WHEN
        try:
            cas_middleware(request)
        except:
            pass

        # THEN
        assert cas_middleware.validate_ticket.call_count == 1

    def test_institution_does_not_exist(self, request_builder):
        """Testing the __call_ method with an unknown institution"""
        # GIVEN
        uai_number = "fake-uai"
        query_params = "/?sso_id={}".format(uai_number)
        request = request_builder.build(query_params)
        request.session["uai_number"] = uai_number
        cas_middleware = CASMiddleware(request)

        # WHEN
        cas_middleware(request)

        # THEN
        assert cas_middleware.get_response.path == "/"

    def test_validate_ticket_with_multiple_institutions(
        self, mock_get_verification_response_with_multiple_institutions, request_builder
    ):
        # GIVEN
        uai_number = "9999999Q"
        query_params = "/?sso_id={}".format(uai_number)
        request = request_builder.build(query_params)
        request.session["uai_number"] = uai_number

        # WHEN
        uai_numbers = CASMiddleware.validate_ticket(request, "dummy-ticket")

        # THEN
        assert uai_number in uai_numbers
        mock_get_verification_response_with_multiple_institutions.assert_called_once()
