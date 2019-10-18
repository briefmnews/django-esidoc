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

    def test_form_works_with_gar_when_creating_instance(
        self, form_data, mocker, response_from_gar
    ):
        # GIVEN
        mock_request = mocker.patch.object(
            requests,
            "request",
            return_value=response_from_gar(201, "dummy response message"),
        )

        # WHEN
        form = InstitutionForm(data=form_data(ent="GAR").data)

        # THEN
        assert mock_request.called_once()
        assert form.is_valid()

    def test_form_error_with_gar_when_creating_instance(
        self, form_data, mocker, response_from_gar
    ):
        # GIVEN
        error_message = "dummy error message"
        mock_request = mocker.patch.object(
            requests, "request", return_value=response_from_gar(400, error_message)
        )

        # WHEN
        form = InstitutionForm(data=form_data(ent="GAR").data)

        # THEN
        assert mock_request.called_once()
        assert not form.is_valid()
        assert error_message in form.errors["ent"]

    def test_form_works_with_gar_when_try_creating_instance_that_already_exists(
        self, form_data, mocker, response_from_gar
    ):
        # GIVEN
        mock_request = mocker.patch.object(
            requests,
            "request",
            side_effect=[
                response_from_gar(409, "Cette abonnement existe deja"),
                response_from_gar(201, "OK"),
            ],
        )

        # WHEN
        form = InstitutionForm(data=form_data(ent="GAR").data)
        # from ipdb import set_trace
        # set_trace()
        form.save()

        # THEN
        assert mock_request.call_count == 2
        assert form.is_valid()

    def test_form_works_with_gar_when_updating_instance(
        self, form_data, mocker, response_from_gar, user
    ):
        # GIVEN
        institution = user.institution
        data = form_data(institution=institution, ent="GAR").data
        institution.ent = "GAR"
        institution.save()
        mock_request = mocker.patch.object(
            requests,
            "request",
            return_value=response_from_gar(200, "dummy response message"),
        )

        # WHEN
        form = InstitutionForm(instance=institution, data=data)
        form.save()

        # THEN
        assert mock_request.called_once()
        assert form.is_valid()

    def test_form_error_with_gar_when_updating_instance(
        self, form_data, mocker, response_from_gar, user
    ):
        # GIVEN
        institution = user.institution
        data = form_data(institution=institution, ent="GAR").data
        institution.ent = "GAR"
        institution.save()
        error_message = "dummy error message"
        mock_request = mocker.patch.object(
            requests, "request", return_value=response_from_gar(400, error_message)
        )

        # WHEN
        form = InstitutionForm(instance=institution, data=data)

        # THEN
        assert mock_request.called_once()
        assert not form.is_valid()
        assert error_message in form.errors["ent"]

    def test_form_deletes_gar_properly_on_changing_ent(
        self, form_data, mocker, response_from_gar, user
    ):
        """
        When an institution using GAR is changed to another ENT
        the subscription needs to be removed in the GAR api
        """
        # GIVEN
        institution = user.institution
        data = form_data(institution=institution, ent="HDF").data
        institution.ent = "GAR"
        institution.save()
        mock_request = mocker.patch.object(
            requests, "delete", return_value=response_from_gar(204, "")
        )

        # WHEN
        form = InstitutionForm(instance=institution, data=data)
        form.save()

        assert mock_request.called_once()
        assert form.is_valid()
