SECRET_KEY = "dump-secret-key"

ROOT_URLCONF = "django_esidoc.urls"

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.admin",
    "django_esidoc",
)


DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3"}}

ESIDOC_ACCESS_TOKEN = "my-secret-token"

ENT_ESIDOC_BASE_URL = "https://{}-cas.esidoc.fr/cas/"
ENT_HDF_BASE_URL = "https://preprod.enthdf.fr/cas"
ESIDOC_QUERY_STRING_TRIGGER = "esidoc_sso_id"
