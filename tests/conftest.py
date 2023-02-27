import datetime
import pytest

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory

from .factories import UserFactory


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def user_without_institution():
    user = UserFactory()
    user.institution.delete()
    return user


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


class RequestBuilder:
    @staticmethod
    def get(path="?"):
        rf = RequestFactory()
        request = rf.get(path)
        request.user = AnonymousUser()

        middleware = SessionMiddleware("dummy")
        middleware.process_request(request)
        request.session.save()

        return request


@pytest.fixture
def mock_verification_response(mocker):
    file = "tests/fixtures/valid_ticket_esidoc.xml"

    with open(file, "r") as xml_response:
        return mocker.patch(
            "cas.CASClientV2.get_verification_response",
            return_value=xml_response.read(),
        )


@pytest.fixture
def form_data():
    return FormDataBuilder


class FormDataBuilder:
    institution = None

    def __init__(self, institution=None):
        self.institution = institution

    @property
    def data(self):
        if self.institution:
            form_data = {
                "uai": self.institution.uai,
                "institution_name": self.institution.institution_name,
                "ends_at": self.institution.ends_at,
                "user": self.institution.user.id,
            }
        else:
            user = UserFactory()
            user.institution.delete()
            form_data = {
                "uai": "00000f",
                "institution_name": "dummy",
                "ends_at": datetime.datetime.today(),
                "user": user.id,
            }

        return form_data
