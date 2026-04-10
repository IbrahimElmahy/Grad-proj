import os
import sys
import django
from django.conf import settings

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rvms_backend.settings")
django.setup()

from django.urls import get_resolver

def show_urls(urllist, depth=0):
    for entry in urllist:
        print("  " * depth + str(entry.pattern))
        if hasattr(entry, 'url_patterns'):
            show_urls(entry.url_patterns, depth + 1)

resolver = get_resolver()
show_urls(resolver.url_patterns)
