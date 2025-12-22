# encyclopedia/storage.py - NEW FILE
"""
Handles reading/writing markdown files and syncing with GitHub
"""
import os
import requests
import base64
from django.conf import settings
import subprocess
from pathlib import Path

def get_entries_dir():
    """Get the path to entries directory"""
    return Path(settings.BASE_DIR) / 'entries'

def get_entry_content(title):
    """Read an entry from MD file"""
    filepath = get_entries_dir() / f"{title}.md"
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        # Remove title header if it's the first line
        if content.startswith(f'# {title}\n'):
            content = content[len(f'# {title}\n'):]
        elif content.startswith(f'# {title}\r\n'):
            content = content[len(f'# {title}\r\n'):]
        return content.strip()
    return None

def save_entry_locally(title, content):
    """Save entry to local MD file"""
    entries_dir = get_entries_dir()
    entries_dir.mkdir(exist_ok=True)
    
    filepath = entries_dir / f"{title}.md"
    
    # Write with title as header
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(content)
    
    return str(filepath)

def get_all_titles():
    """Get all entry titles from local MD files"""
    entries_dir = get_entries_dir()
    titles = []
    if entries_dir.exists():
        for file in entries_dir.iterdir():
            if file.suffix == '.md':
                titles.append(file.stem)  # Remove .md extension
    return sorted(titles)

# In encyclopedia/storage.py - REPLACE the sync_with_github function
def sync_with_github(title, content, username):
    """
    Save locally AND push to GitHub WITHOUT pulling first.
    This avoids the "unstaged changes" error.
    """
    try:
        # 1. ALWAYS save locally first (critical for app to work)
        save_entry_locally(title, content)
        print(f"✅ Saved '{title}' locally")
        
        # 2. Check if GitHub sync is configured
        if not GITHUB_TOKEN or not GITHUB_REPO_OWNER or not GITHUB_REPO_NAME:
            print("⚠️ GitHub credentials missing - local save only")
            return False
        
        # 3. DIRECT GitHub API push (no git pull needed)
        print(f"🔄 Pushing '{title}' directly to GitHub...")
        
        # Prepare the API request
        api_url = f'https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/contents/entries/{title}.md'
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Read the file we just saved locally
        entry_path = os.path.join('entries', f'{title}.md')
        with open(entry_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        # Convert to base64 for GitHub API
        import base64
        content_base64 = base64.b64encode(file_content.encode('utf-8')).decode('utf-8')
        
        # 4. First, check if file exists on GitHub to get its SHA
        response = requests.get(api_url, headers=headers, timeout=10)
        sha = None
        
        if response.status_code == 200:
            # File exists - get SHA for update
            sha = response.json().get('sha')
            print(f"📝 Updating existing file on GitHub (SHA: {sha[:8]}...)")
            commit_message = f'Update {title} via wiki by {username}'
        elif response.status_code == 404:
            # File doesn't exist - create new
            print(f"📝 Creating new file on GitHub")
            commit_message = f'Create {title} via wiki by {username}'
        else:
            print(f"⚠️ GitHub API error: {response.status_code}")
            return False
        
        # 5. Push to GitHub (create or update)
        payload = {
            'message': commit_message,
            'content': content_base64,
            'branch': 'main'
        }
        
        if sha:  # Add SHA if updating existing file
            payload['sha'] = sha
        
        response = requests.put(api_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"✅ GitHub commit successful: {data['commit']['html_url']}")
            return True
        else:
            print(f"❌ GitHub push failed: {response.status_code} - {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"💥 Error in GitHub sync: {e}")
        return False

# In encyclopedia/storage.py
def git_pull_latest():
    """
    SAFE git pull - only runs if no local changes exist.
    Called on startup to get latest content.
    """
    try:
        # Skip if not a git repo or on Render build
        if not os.path.exists('.git') or os.environ.get('RENDER'):
            return True
            
        import subprocess
        
        # Check if there are uncommitted changes
        status = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        # Only pull if workspace is clean
        if not status.stdout.strip():
            print("🔄 Pulling latest from GitHub (clean workspace)...")
            result = subprocess.run(
                ['git', 'pull', 'origin', 'main', '--ff-only'],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            if result.returncode == 0:
                print("✅ Pull successful")
                return True
            else:
                print(f"⚠️ Pull failed: {result.stderr}")
                return False
        else:
            print(f"⚠️ Skipping git pull - local changes detected")
            print(f"Changes: {status.stdout}")
            return False  # Don't overwrite user edits!
            
    except Exception as e:
        print(f"⚠️ Git pull error (non-critical): {e}")
        return True  # Don't crash app on git errors
