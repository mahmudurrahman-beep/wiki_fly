# UPDATED encyclopedia/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
import re

# Import storage functions
from .storage import get_entry_content, save_entry_locally, sync_with_github

class EntryManager(models.Manager):
    def list_entries(self, user=None):
        """Returns list of all entry names (from files, not database)"""
        from .storage import get_all_titles
        return get_all_titles()

    def get_entry(self, title, user=None):
        """Get entry by title (from files)"""
        content = get_entry_content(title)
        if content:
            # Return a dummy entry object if needed
            class DummyEntry:
                def __init__(self, title, content):
                    self.title = title
                    self.content = content
                    self.user = user or User.objects.first()
            return DummyEntry(title, content)
        return None

    def save_entry(self, title, content, user):
        """Save entry to both files and database (for history)"""
        # 1. Save to local file
        filepath = save_entry_locally(title, content)
        
        # 2. Sync to GitHub
        sync_success = sync_with_github(title, content, user.username)
        
        # 3. Save to database for history tracking (optional)
        entry, created = Entry.objects.update_or_create(
            user=user,
            title=title,
            defaults={'content': content}
        )
        
        return entry

class Entry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entries')
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = EntryManager()

    class Meta:
        unique_together = ['user', 'title']

    def __str__(self):
        return f"{self.title} (by {self.user.username})"
