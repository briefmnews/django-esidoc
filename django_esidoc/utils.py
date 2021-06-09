import logging

from django.conf import settings

from cas import CASClient

logger = logging.getLogger(__name__)

ESIDOC_INACTIVE_USER_REDIRECT = getattr(settings, "ESIDOC_INACTIVE_USER_REDIRECT", "/")
ENT_ESIDOC_BASE_URL = getattr(settings, "ENT_ESIDOC_BASE_URL", "{}")
ESIDOC_QUERY_STRING_TRIGGER = getattr(
    settings, "ESIDOC_QUERY_STRING_TRIGGER", "esidoc_sso_id"
)


def get_redirect_url(request, path=None):
    """Get redirect url for cas"""

    scheme = request.scheme
    host = request.get_host()
    if path:
        url = "{}://{}{}".format(scheme, host, path)
    else:
        url = "{}://{}".format(scheme, host)

    return url


def get_cas_client(request):
    """Create a CAS client"""

    uai_number = request.session.get("uai_number")
    logger.info(f"e-sidoc; uai: {uai_number}")

    server_url = ENT_ESIDOC_BASE_URL.format(uai_number)

    next_page = request.get_full_path()
    service_url = get_redirect_url(request, next_page)

    client = CASClient(version=2, server_url=server_url, service_url=service_url)

    return client
