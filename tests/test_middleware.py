# -*- coding: utf-8 -*-
import pytest

from django.conf import settings

from django_esidoc.middleware import CASMiddleware

pytestmark = pytest.mark.django_db

ESIDOC_DEFAULT_REDIRECT = getattr(settings, 'ESIDOC_DEFAULT_REDIRECT', '/')


class TestCASMiddleware(object):

    @staticmethod
    def test_init():
        """Testing the __init__ method"""
        # WHEN
        cas_middleware = CASMiddleware('dump_response')

        # THEN
        assert cas_middleware.get_response == 'dump_response'

    def test_no_uai_no_ticket(self, request_builder):
        """Testing the middleware if not a connection to esidoc"""
        # GIVEN
        cas_middleware = CASMiddleware(request_builder.build)

        # WHEN
        response = cas_middleware(request_builder.build())

        # THEN
        assert cas_middleware.get_response().path == u'/'
        assert 'sso_id' not in response.GET
        assert 'ticket' not in response.GET

    @staticmethod
    def test_when_uai_number(user, request_builder):
        """Testing the __call__ method with uai_number in url"""
        # GIVEN
        uai_number = user.institution.uai
        query_params = '/?sso_id={}'.format(uai_number)
        request = request_builder.build(query_params)
        cas_middleware = CASMiddleware(request)

        # WHEN
        response = cas_middleware(request)

        # THEN
        assert 'https://{}.esidoc.fr'.format(uai_number) in response.url

    def test_when_cas_ticket_valid(self, mock_validate_valid_ticket, user, request_builder):
        """
        Testing the __call__ method with valid cas_ticket in url and user
        has access (is_active is True)
        """
        # GIVEN
        uai_number = user.institution.uai
        cas_ticket = 'this-is-a-ticket'
        query_params = '/?ticket={}'.format(cas_ticket)
        request = request_builder.build(query_params)
        request.session['uai_number'] = uai_number
        cas_middleware = CASMiddleware(request)

        # WHEN
        try:
            cas_middleware(request)
        except:
            pass

        # THEN
        assert cas_middleware.validate_ticket.call_count == 1

    def test_when_cas_ticket_invalid(self, mock_validate_invalid_ticket, user, request_builder):
        """
        Testing the __call__ method with cas_ticket in url and user
        has access (is_active is True)
        """
        # GIVEN
        uai_number = user.institution.uai
        cas_ticket = 'this-is-a-ticket'
        query_params = '/?ticket={}'.format(cas_ticket)
        request = request_builder.build(query_params)
        request.session['uai_number'] = uai_number
        cas_middleware = CASMiddleware(request)

        # WHEN
        try:
            cas_middleware(request)
        except:
            pass

        # THEN
        assert cas_middleware.validate_ticket.call_count == 1
