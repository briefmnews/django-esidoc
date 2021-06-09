import logging

from django.conf import settings

from cas import CASClient, CASClientV2

logger = logging.getLogger(__name__)

ESIDOC_INACTIVE_USER_REDIRECT = getattr(settings, "ESIDOC_INACTIVE_USER_REDIRECT", "/")
ENT_ESIDOC_BASE_URL = getattr(settings, "ENT_ESIDOC_BASE_URL", "{}")
ENT_HDF_BASE_URL = getattr(settings, "ENT_HDF_BASE_URL", "")
ENT_OCCITANIE_BASE_URL = getattr(settings, "ENT_OCCITANIE_BASE_URL", "")
ENT_OCCITANIEAGR_BASE_URL = getattr(settings, "ENT_OCCITANIEAGR_BASE_URL", "")
ENT_CORRELYCE_BASE_URL = getattr(settings, "ENT_CORRELYCE_BASE_URL", "")
ENT_GMINVENT_BASE_URL = getattr(settings, "ENT_GMINVENT_BASE_URL", "")
ENT_C3RB_BASE_URL = getattr(settings, "ENT_C3RB_BASE_URL", "")
ESIDOC_QUERY_STRING_TRIGGER = getattr(settings, "ESIDOC_QUERY_STRING_TRIGGER", "esidoc_sso_id")

BASE_URLS = {
    "ESIDOC": ENT_ESIDOC_BASE_URL,
    "OCCITANIE": ENT_OCCITANIE_BASE_URL,
    "OCCITANIEAGR": ENT_OCCITANIEAGR_BASE_URL,
    "CORRELYCE": ENT_CORRELYCE_BASE_URL,
    "HDF": ENT_HDF_BASE_URL,
    "GMINVENT": ENT_GMINVENT_BASE_URL,
    "C3RB": ENT_C3RB_BASE_URL,
}


def get_redirect_url(request, path=None):
    """Get redirect url for cas"""

    scheme = request.scheme
    host = request.get_host()
    if request.session.get("ent") in ["OCCITANIE", "OCCITANIEAGR"]:
        url = "{}://{}/?{}={}".format(
            scheme, host, ESIDOC_QUERY_STRING_TRIGGER, request.session.get("ent").lower()
        )
    elif request.session.get("ent") == "CORRELYCE":
        url = "{}://{}/?uai={}&pf=atrium-paca".format(
            scheme, host, request.session.get("uai_number").upper()
        )
    elif path:
        url = "{}://{}{}".format(scheme, host, path)
    else:
        url = "{}://{}".format(scheme, host)

    return url


def get_cas_client(request):
    """Create a CAS client"""

    uai_number = request.session.get("uai_number")
    ent = request.session.get("ent")
    logger.info(f"ent: {ent}; uai: {uai_number}")
    cas_version = 2

    server_url = BASE_URLS.get(ent, ENT_HDF_BASE_URL).format(uai_number)

    next_page = request.get_full_path()
    service_url = get_redirect_url(request, next_page)

    if ent == "CORRELYCE":
        client = CASClientCorrelyce(server_url=server_url, service_url=service_url)
    else:
        client = CASClient(
            version=cas_version, server_url=server_url, service_url=service_url
        )

    return client


class CASClientCorrelyce(CASClientV2):
    url_suffix = "proxyValidate"
