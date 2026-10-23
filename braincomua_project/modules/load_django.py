"""
Sets up Django so that scripts from the modules folder can use the project models
"""

import os
import sys
import django

sys.path.append('/Users/rimmyraa/PycharmProjects/braincomua_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'braincomua_project.settings')
django.setup()