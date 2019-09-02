# -*- coding: utf-8 -*-
import pytest

from django.contrib.auth import get_user_model

from django_esidoc.backends import CASBackend

pytestmark = pytest.mark.django_db


class TestCASBackend(object):
    @staticmethod
    def test_user_has_access(user):
        """
        Test the case where user has access (is_active = True)
        """
        # WHEN
        backend = CASBackend()
        authenticated_user = backend.authenticate(
            request=None, uai_number=user.institution.uai
        )

        # THEN
        assert authenticated_user is not None
        assert authenticated_user.email == user.email

    @staticmethod
    def test_user_doesnt_have_access(user):
        """
        Test the case where user doesn't have access (is_active = False)
        """
        # GIVEN
        user.is_active = False
        user.save()

        # WHEN
        backend = CASBackend()
        authenticated_user = backend.authenticate(
            request=None, uai_number=user.institution.uai
        )

        # THEN
        assert authenticated_user is None

    @staticmethod
    def test_get_user_works(user):
        """
        Test the case where get_user find the corresponding user in the database
        """
        # WHEN
        backend = CASBackend()
        authenticated_user = backend.get_user(user_id=user.id)

        # THEN
        assert authenticated_user is not None

    @staticmethod
    def test_get_user_fails(user):
        """
        Test the case where get_user couldn't find the corresponding user in the database
        """
        # GIVEN
        UserModel = get_user_model()
        last_user = UserModel.objects.last()

        # WHEN
        backend = CASBackend()
        user = backend.get_user(user_id=last_user.id + 1)

        # THEN
        assert user is None
