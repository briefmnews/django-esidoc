import requests

from django.conf import settings


ENT_GAR_SUBSCRIPTION_PREFIX = getattr(settings, "ENT_GAR_SUBSCRIPTION_PREFIX", "")
ENT_GAR_BASE_SUBSCRIPTION_URL = getattr(settings, "ENT_GAR_BASE_SUBSCRIPTION_URL", "")

ENT_GAR_CERTIFICATE_PATH = getattr(settings, "ENT_GAR_CERTIFICATE_PATH", "")
ENT_GAR_KEY_PATH = getattr(settings, "ENT_GAR_KEY_PATH", "")


def delete_gar_subscription(uai):
    url = get_gar_request_url(uai)
    cert = get_gar_certificate()
    headers = get_gar_headers()
    requests.delete(url, cert=cert, headers=headers)


def get_gar_subscription_id(uai):
    """
    The id of the subscription in the GAR.
    It needs to be unique even among all organizations
    """
    subscription_id = "{}{}".format(ENT_GAR_SUBSCRIPTION_PREFIX, uai)
    return subscription_id


def get_gar_request_url(uai):
    base_url = ENT_GAR_BASE_SUBSCRIPTION_URL
    subscription_id = get_gar_subscription_id(uai)
    url = "{}{}".format(base_url, subscription_id)
    return url


def get_gar_certificate():
    cert = (ENT_GAR_CERTIFICATE_PATH, ENT_GAR_KEY_PATH)
    return cert


def get_gar_headers():
    headers = {"Content-Type": "application/xml"}
    return headers
