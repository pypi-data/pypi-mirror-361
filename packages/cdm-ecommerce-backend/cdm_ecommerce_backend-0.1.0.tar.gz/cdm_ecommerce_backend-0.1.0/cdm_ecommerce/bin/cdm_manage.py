#!/usr/bin/env python3

"""Django's command-line utility for administrative tasks."""

import os
import sys


def main() -> None:
    """Run administrative tasks."""
    if "test" in sys.argv:
        os.environ.setdefault(
            "DJANGO_SETTINGS_MODULE", "tests.config.settings"
        )
    else:
        os.environ.setdefault(
            "DJANGO_SETTINGS_MODULE", "cdm_ecommerce.config.settings"
        )

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
