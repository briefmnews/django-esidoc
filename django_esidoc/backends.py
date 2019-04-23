# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model

User = get_user_model()


class CASBackend(object):
    """
    CAS authentication with UAI (Unité Administrative Immatriculée) number
    """
    @staticmethod
    def authenticate(uai_number):
        try:
            user = User.objects.get(
                institution__uai=uai_number,
                is_active=True
            )
            return user
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_user(user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
