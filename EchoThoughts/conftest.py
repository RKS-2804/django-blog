import os
import django
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EchoThoughts.settings")
django.setup()

# @pytest.fixture(scope="session", autouse=True)
# def django_setup():
#     """Ensure Django is properly initialized before tests run."""
#     django.setup()
