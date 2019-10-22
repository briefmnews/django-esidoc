from django.conf import settings

from cas import CASClient

ESIDOC_INACTIVE_USER_REDIRECT = getattr(settings, "ESIDOC_INACTIVE_USER_REDIRECT", "/")
ENT_GAR_BASE_URL = getattr(settings, "ENT_GAR_BASE_URL", "")
ENT_ESIDOC_BASE_URL = getattr(settings, "ENT_ESIDOC_BASE_URL", "{}")
ENT_HDF_BASE_URL = getattr(settings, "ENT_HDF_BASE_URL", "")
ENT_QUERY_STRING_TRIGGER = getattr(settings, "ENT_QUERY_STRING_TRIGGER", "sso_id")


def get_redirect_url(request, path=None):
    """Get redirect url for cas"""

    scheme = request.scheme
    host = request.get_host()
    if request.session.get("ent") == "GAR":
        url = "{}://{}/?{}={}".format(scheme, host, ENT_QUERY_STRING_TRIGGER, "gar")
    elif path:
        url = "{}://{}{}".format(scheme, host, path)
    else:
        url = "{}://{}".format(scheme, host)

    return url


def _get_cas_base_url(uai_number, ent):
    """Get the CAS base url format depending on the ENT"""

    if ent == "GAR":
        url = ENT_GAR_BASE_URL
    elif ent == "ESIDOC":
        url = ENT_ESIDOC_BASE_URL.format(uai_number)
    else:
        url = ENT_HDF_BASE_URL

    return url


def get_cas_client(request):
    """Create a CAS client"""

    uai_number = request.session.get("uai_number")
    ent = request.session.get("ent")
    if ent == "GAR":
        cas_version = 3
    else:
        cas_version = 2

    server_url = _get_cas_base_url(uai_number, ent)

    next_page = request.path
    service_url = get_redirect_url(request, next_page)

    client = CASClient(
        version=cas_version, server_url=server_url, service_url=service_url
    )

    return client
