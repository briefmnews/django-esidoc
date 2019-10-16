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
    return mocker.patch(
        "django_esidoc.middleware.CASMiddleware.validate_ticket",
        return_value=user.institution.uai,
    )


@pytest.fixture
def mock_validate_invalid_ticket(mocker):
    return mocker.patch(
        "django_esidoc.middleware.CASMiddleware.validate_ticket", return_value=[]
    )


@pytest.fixture
def request_builder():
    """Create a request object"""
    return RequestBuilder()


class RequestBuilder(object):
    @staticmethod
    def get(path="?"):
        rf = RequestFactory()
        request = rf.get(path)
        request.user = AnonymousUser()

        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        return request


@pytest.fixture
def mock_verification_response(mocker, ent):
    if ent == "GAR":
        file = "tests/fixtures/valid_ticket_gar.xml"
    elif ent == "ESIDOC":
        file = "tests/fixtures/valid_ticket_esidoc.xml"
    else:
        file = "tests/fixtures/valid_ticket_hdf_with_multiple_institutions.xml"

    with open(file, "r") as xml_response:
        return mocker.patch(
            "cas.CASClientV2.get_verification_response",
            return_value=xml_response.read(),
        )
