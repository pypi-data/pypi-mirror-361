import random

from django.conf import settings
from django.core.management import call_command

from ebird.api.requests import get_regions
from faker import Faker

import pytest

pytestmark = pytest.mark.django_db


@pytest.fixture()
def region():
    country = Faker().country_code()
    if regions := get_regions(settings.EBIRD_API_KEY, "subnational1", country):
        codes = [region["code"] for region in regions]
        code = random.choice(codes)
    else:
        code = country
    return code


def test_loader(region):
    call_command("add_checklists", "--days", 2, region)
