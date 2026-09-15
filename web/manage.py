#!/usr/bin/env python3
"""Django entrypoint for the DSA Knowledge Base UI."""
import os
import sys


def main():
    web_dir = os.path.dirname(os.path.abspath(__file__))
    if web_dir not in sys.path:
        sys.path.insert(0, web_dir)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
