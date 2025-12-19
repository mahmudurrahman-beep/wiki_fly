"""
Import script for wiki entries.
Optimized for Render.com deployment
"""

import os
import sys
import django
from pathlib import Path
import shutil

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wiki.settings')
django.setup()

from encyclopedia.util import save_entry, get_entry, list_entries, ensure_entries_directory
from encyclopedia.models import Entry
from django.contrib.auth.models import User
from django.conf import settings

# ====== SAMPLE ENTRIES (FIXED VERSION) ======
SAMPLE_ENT
