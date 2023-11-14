from django.contrib.auth import get_user_model

User = get_user_model()


class CASBackend:
    """
    CAS authentication with UAI (Unité Administrative Immatriculée) number
    """

    @staticmethod
    def authenticate(request, esidoc_uai_numbers):
        return User.objects.filter(institution__uai__in=esidoc_uai_numbers).last()

    @staticmethod
    def get_user(user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
