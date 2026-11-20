"""
Script for initializing the Django environment to run external parsers from the modules folder.
"""
import os
import sys

import django

# Add the root directory of the Django project (where manage.py is located) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ['DJANGO_SETTINGS_MODULE'] = 'braincomua_project.settings'
django.setup()
