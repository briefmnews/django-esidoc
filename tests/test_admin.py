import pytest
import requests

from django.contrib.admin.sites import AdminSite

from django_esidoc.admin import InstitutionAdmin
from django_esidoc.models import Institution

pytestmark = pytest.mark.django_db


class TestInstitutionAdmin:
    def test_gar_subscription_is_deleted_via_api(self, mocker, request_builder, user):
        # GIVEN
        institution = user.institution
        institution.ent = "GAR"
        institution.save()
        request = request_builder.get()
        mock_request = mocker.patch.object(requests, "delete", return_value="OK")

        # WHEN
        institution = InstitutionAdmin(Institution, AdminSite()).delete_model(
            request=request, obj=institution
        )

        # THEN
        assert not institution
        assert mock_request.called_once()
