from cas import CASClient


def get_redirect_url(request, path=None):
    """Get redirect url for cas"""

    scheme = request.scheme
    host = request.get_host()
    if path:
        url = "{}://{}{}".format(scheme, host, path)
    else:
        url = "{}://{}".format(scheme, host)

    return url


def _get_cas_base_url(uai_number):
    """Get the CAS base url format"""
    return "https://{}.esidoc.fr/cas/".format(uai_number)


def get_cas_client(request):
    """Create a CAS client"""

    uai_number = request.session.get("uai_number")
    server_url = _get_cas_base_url(uai_number)

    next_page = request.path
    service_url = get_redirect_url(request, next_page)

    client = CASClient(version=2, server_url=server_url, service_url=service_url)

    return client
