#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    # Agregar publishtracker/apps al PYTHONPATH
    current_dir = os.path.dirname(os.path.abspath(__file__))
    apps_path = os.path.join(current_dir, 'publishtracker', 'apps')
    sys.path.insert(0, apps_path)
    
    # También agregar publishtracker para que encuentre el paquete apps
    publishtracker_path = os.path.join(current_dir, 'publishtracker')
    sys.path.insert(0, publishtracker_path)

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
