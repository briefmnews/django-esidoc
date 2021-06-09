# django-esidoc
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-270/) 
[![Django 2.2](https://img.shields.io/badge/django-2.2-blue.svg)](https://docs.djangoproject.com/en/2.2/)
[![Build Status](https://travis-ci.org/briefmnews/django-esidoc.svg?branch=master)](https://travis-ci.org/briefmnews/django-esidoc)
[![codecov](https://codecov.io/gh/briefmnews/django-esidoc/branch/master/graph/badge.svg)](https://codecov.io/gh/briefmnews/django-esidoc)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)  
Handle CAS login via sso for french ENT (Etablissements Numériques de Travail) like 
[e-sidoc](https://www.reseau-canope.fr/notice/e-sidoc.html) or ENT Hauts-de-France (HDF) or Occitanie (OCCITANIE) or Occitanie lycée agricole (OCCITANIEAGR)
or (GMINVENT) GMInvent or (C3RB) C3rb.

## Installation
Install with [pip](https://pip.pypa.io/en/stable/):
```shell
pip install -e git://github.com/briefmnews/django-esidoc.git@master#egg=django_esidoc
```

## Setup
In order to make `django-esidoc` works, you'll need to follow the steps below.

### Settings
First you need to add the following configuration to your settings:
```python
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',

    'django_esidoc',
    ...
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    
    'django_esidoc.middleware.CASMiddleware',
    ...
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    
    'django_esidoc.backends.CASBackend',
    ...
)
```

### Url
Then you need to add the `logout` url to your `urls.py`
```python
urlpatterns = [
    ...,
    url(r'^esidoc/', include('django_esidoc.urls')),
    ...
]
```
To logout an user, with the example above, you need to call `esidoc/logout/`. 
You could call `django_esidoc_logout` as well.

### Migrations
Next, you need to run the migrations in order to update your database schema.
```shell
python manage.py migrate
```

### Mandatory settings
Here is the list of all the mandatory settings:
```python
ENT_ESIDOC_BASE_URL
ENT_HDF_BASE_URL
ENT_OCCITANIE_BASE_URL
ENT_OCCITANIEAGR_BASE_URL
ESIDOC_QUERY_STRING_TRIGGER
```

### Optional settings - Default redirection
You can set a default path redirection for inactive user by adding this line to 
your settings:
```python
ESIDOC_INACTIVE_USER_REDIRECT = '/{mycustompath}/'
```
`ESIDOC_INACTIVE_USER_REDIRECT` is used if an inactive user with a valid ticket
tries to login.
If `ESIDOC_INACTIVE_USER_REDIRECT` is not set in the settings, it will take
the root path (i.e. `/`) as default value.


## How to use ?
Once your all set up, when a request to your app is made with the query string 
`esidoc_sso_id=<unique_uai>`, the `CASMiddleware` catches the request and start the login process. 
Here is an example of a request url to start the login process:
```http request
https://www.exemple.com/?esidoc_sso_id=9990075c
```

## API endpoint (only for Esidoc)
In order to expose the `Institutions` UAI number and end of subscription date, the following
API endpoint is available:
```python
urlpatterns = [
    ...,
    
    url(r"^institutions/$", InstitutionViewSet.as_view({'get': 'list'}), name="esidoc_institutions")
]
```
This endpoint is protected by a query string token authentication named `token`. 
The token value can be set in the settings.py of your app.
```python
ESIDOC_ACCESS_TOKEN = 'my-secret-token-value'
```
Now when calling `/esidoc/insitutions/?token=my-secret-token-value`, you will get a json response
with all your uai numbers (`uai`) and ends of subscription (`ends_at`). Here is an example:
```json
[
    {
        "uai": "9990075C",
        "ends_at": "2020-10-05"
    },
    {
        "uai": "8880075C",
        "ends_at": "2021-09-01"
    }
]
```

## Tests
Testing is managed by `pytest`. Required package for testing can be installed with:
```shell
pip install -r test_requirements.txt
```
To run testing locally:
```shell
pytest
```

## Credits
- [python-cas](https://github.com/python-cas/python-cas)
- [django-cas-ng](https://github.com/mingchen/django-cas-ng)

## References
- [CAS protocol](https://www.apereo.org/projects/cas)
- [e-sidoc](https://www.reseau-canope.fr/notice/e-sidoc.html)
