import datetime
import factory

from django.contrib.auth import get_user_model

from django_esidoc.models import Institution


class InstitutionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Institution

    institution_name = factory.Sequence(lambda n: "Lycée {0}".format(n))
    uai = factory.Sequence(lambda n: "{0}".format(n))
    ends_at = datetime.datetime.today()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: "noel{0}@flantier.com".format(n))
    is_active = True
    institution = factory.RelatedFactory(InstitutionFactory, "user")
