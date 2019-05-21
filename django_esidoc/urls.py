from django.conf.urls import url

from .views import LogoutRedirectView


urlpatterns = [url(r"^logout/$", LogoutRedirectView.as_view(), name="esidoc_logout")]
