import pytest

from django_esidoc.forms import InstitutionForm

pytestmark = pytest.mark.django_db


class TestInstitutionForm:
    def test_form_works_properly(self, form_data):
        # GIVEN
        form_data = form_data().data

        # WHEN
        form = InstitutionForm(data=form_data)

        # THEN
        assert form.is_valid()
