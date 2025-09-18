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

    def test_institution_name_transformation(self):
        # GIVEN
        form_data = {
            "uai": "00000F",
            "institution_name": "Lycée Saint-Éxupéry",
            "ends_at": "2025-12-31",
            "user": 1,
        }

        # WHEN
        form = InstitutionForm(data=form_data)
        form.is_valid()

        # THEN
        assert form.cleaned_data["institution_name"] == "LYCEE SAINT-EXUPERY"
