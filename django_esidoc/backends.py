from django.contrib.auth import get_user_model

User = get_user_model()


class CASBackend:
    """
    CAS authentication with UAI (Unité Administrative Immatriculée) number
    """

    @staticmethod
    def authenticate(request, uai_numbers):
        user = User.objects.filter(
            institution__uai__in=uai_numbers, is_active=True
        ).last()
        return user

    @staticmethod
    def get_user(user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
