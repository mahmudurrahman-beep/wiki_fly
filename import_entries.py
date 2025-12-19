import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wiki.settings')
django.setup()

from encyclopedia.models import Entry
from django.contrib.auth.models import User
from encyclopedia.util import list_entries, get_entry, save_entry

def create_sample_entries():
    """Create sample entries if none exist"""
    samples = {
        "CSS": "# CSS\n\nCascading Style Sheets is a style sheet language.",
        "Django": "# Django\n\nDjango is a high-level Python web framework.",
        "Git": "# Git\n\nGit is a distributed version control system.",
        "HTML": "# HTML\n\nHTML is the standard markup language.",
        "Python": "# Python\n\nPython is a programming language.",
        "Generative AI": "# Generative AI\n\nGenerative AI creates new content."
    }
    
    for title, content in samples.items():
        save_entry(title, content)
        print(f"📝 Created file: {title}")
    
    return list(samples.keys())

def import_markdown_entries():
    """Import all Markdown files into database"""
    
    # Get or create admin user
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={'email': 'admin@example.com', 'is_staff': True}
    )
    if created:
        user.set_password('admin123')
        user.save()
        print("👤 Created admin user (password: admin123)")
    
    # Get entries (creates samples if none)
    entries = list_entries()
    if not entries:
        print("📁 No entries found, creating samples...")
        entries = create_sample_entries()
    
    print(f"📚 Found {len(entries)} entries")
    
    imported = 0
    for entry_title in entries:
        if not Entry.objects.filter(title=entry_title).exists():
            content = get_entry(entry_title)
            if content:
                Entry.objects.create(
                    user=user,
                    title=entry_title,
                    content=content
                )
                imported += 1
                print(f"✅ Imported: {entry_title}")
        else:
            print(f"📌 Already exists: {entry_title}")
    
    print(f"\n🎯 Import complete! {imported} new entries imported.")
    print(f"📊 Total in database: {Entry.objects.count()}")

if __name__ == '__main__':
    import_markdown_entries()
