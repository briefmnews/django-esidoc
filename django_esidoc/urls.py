from django.conf.urls import url

from .views import InstitutionViewSet, LogoutRedirectView


urlpatterns = [
    url(r"^logout/$", LogoutRedirectView.as_view(), name="esidoc_logout"),
    url(r"^institutions/$", InstitutionViewSet.as_view({'get': 'list'}), name="esidoc_institutions")
]
