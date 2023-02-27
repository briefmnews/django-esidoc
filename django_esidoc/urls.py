from django.urls import re_path

from .views import InstitutionViewSet, LogoutRedirectView


urlpatterns = [
    re_path(r"^logout/$", LogoutRedirectView.as_view(), name="esidoc_logout"),
    re_path(
        r"^institutions/$",
        InstitutionViewSet.as_view({"get": "list"}),
        name="esidoc_institutions",
    ),
]
