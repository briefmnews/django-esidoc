# -*- coding: utf-8 -*-
import pytest

from django_esidoc.apps import DjangoEsidocConfig

pytestmark = pytest.mark.django_db


class TestDjangoEsidocConfig(object):
    @staticmethod
    def test_apps():
        assert 'django_esidoc' in DjangoEsidocConfig.name
