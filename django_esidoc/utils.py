from django.conf import settings

from cas import CASClient

ESIDOC_INACTIVE_USER_REDIRECT = getattr(settings, "ESIDOC_INACTIVE_USER_REDIRECT", "/")


def get_redirect_url(request, path=None):
    """Get redirect url for cas"""

    scheme = request.scheme
    host = request.get_host()
    if path:
        url = "{}://{}{}".format(scheme, host, path)
    else:
        url = "{}://{}".format(scheme, host)

    return url


def _get_cas_base_url(uai_number, ent):
    """Get the CAS base url format depending on the ENT"""

    if ent == "ESIDOC":
        url = "https://{}-cas.esidoc.fr/cas/".format(uai_number)
    elif ent == "GAR":
        url = "https://idp-auth.partenaire.test-gar.education.fr/"
    else:
        url = "https://enthdf.fr/cas/"

    return url


def get_cas_client(request):
    """Create a CAS client"""

    uai_number = request.session.get("uai_number")
    ent = request.session.get("ent")
    server_url = _get_cas_base_url(uai_number, ent)

    next_page = request.path
    service_url = get_redirect_url(request, next_page)

    client = CASClient(version=2, server_url=server_url, service_url=service_url)

    return client
