import pytest
import requests

from django_esidoc.forms import InstitutionForm

pytestmark = pytest.mark.django_db


class TestInstitutionForm:
    @pytest.mark.parametrize("ent", ["ESIDOC", "HDF"])
    def test_form_works_properly(self, ent, form_data):
        # GIVEN
        form_data = form_data(ent=ent).data

        # WHEN
        form = InstitutionForm(data=form_data)

        # THEN
        assert form.is_valid()
