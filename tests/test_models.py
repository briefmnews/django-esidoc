import pytest

from django.db import IntegrityError

from .factories import InstitutionFactory

pytestmark = pytest.mark.django_db


class TestInstitutionModel(object):
    def test_instituion_has_unique_uai_number(self, user):
        uai = user.institution.uai
        with pytest.raises(IntegrityError):
            InstitutionFactory(uai=uai, user=user)
