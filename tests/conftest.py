# -*- coding: utf-8 -*-
import pytest

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory

from .factories import UserFactory


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def mock_validate_valid_ticket(mocker, user):
    mocker.patch(
        'django_esidoc.middleware.CASMiddleware.validate_ticket',
        return_value=user.institution.uai
    )


@pytest.fixture
def mock_validate_invalid_ticket(mocker):
    mocker.patch(
        'django_esidoc.middleware.CASMiddleware.validate_ticket',
        return_value=None
    )


@pytest.fixture
def request_builder():
    """Create a request object"""
    return RequestBuilder()


class RequestBuilder(object):
    @staticmethod
    def build(query_params='?'):
        rf = RequestFactory()
        request = rf.get(query_params)
        request.user = AnonymousUser()

        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        return request
