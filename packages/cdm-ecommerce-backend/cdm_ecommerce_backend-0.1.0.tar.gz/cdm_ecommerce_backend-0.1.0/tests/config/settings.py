"""Test settings for pytest."""

from django.db.backends.postgresql.psycopg_any import IsolationLevel

from cdm_ecommerce.config.settings import *  # noqa

in_github_ci = get_bool_env("GITHUB_CI")  # noqa

ENVIRONMENT = "test"
DEBUG = False
ALLOWED_HOSTS = ["*"]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "cdm_ecommerce_db",
        "USER": "app",
        "PASSWORD": "app",
        "HOST": "postgres" if in_github_ci else "localhost",
        "PORT": "5432",
        "CONN_MAX_AGE": 60,
        "OPTIONS": {
            "isolation_level": IsolationLevel.READ_COMMITTED,
        },
    }
}
