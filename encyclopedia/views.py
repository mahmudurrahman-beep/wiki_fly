from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Entry
from .history_storage import save_to_history, load_from_history
import markdown2
import random
import re
import os
from django.core.cache import cache
import time

# ============ IMPORT STORAGE FUNCTIONS LATER ============
# We'll import these INSIDE the functions that need them
# This avoids circular import issues

# ============ STARTUP SYNC ============
def startup_sync():
    """Startup sync - FIXED VERSION (no circular imports)"""
    if os.environ.get('RENDER') and not os.environ.get('SYNC_DONE'):
        print("🚀 Wiki starting up...")
        
        # Create directories first
        os.makedirs('entries', exist_ok=True)
        os.makedirs('history', exist_ok=True)
        
        # Try git pull LATER (not on import)
        print("✅ Directories created - wiki ready")
        os.environ['SYNC_DONE'] = '1'

# Call sync but don't import storage yet
startup_sync()

# ============ AUTHENTICATION VIEWS ============

def register_view(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        email = request.POST.get('email', '').strip()

        if not username or not password:
            messages.error(request, "Username and password are required")
        elif len(username) < 3:
            messages.error(request, "Username must be at least 3 characters")
        elif len(password) < 6:
            messages.error(request, "Password must be at least 6 characters")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
        else:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email if email else ''
            )
            login(request, user)
            messages.success(request, f"Welcome, {username}! You can now create and edit pages.")
            return redirect('index')

    return render(request, 'encyclopedia/register.html', {'user': request.user})

def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'encyclopedia/login.html', {'user': request.user})

def logout_view(request):
    """User logout"""
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out.")
    return redirect('index')

# ============ WIKI VIEWS ============

def index(request):
    """Home page showing UNIQUE entry titles"""
    # Import INSIDE the function to avoid circular imports
    from .storage import get_all_titles
    titles = get_all_titles()
    return render(request, 'encyclopedia/index.html', {
        'entries': titles,
        'user': request.user
    })

def entry(request, title):
    """Display individual entry (from files)"""
    from .storage import get_entry_content
    content = get_entry_content(title)
    
    if content is None:
        return render(request, 'encyclopedia/error.html', {
            'message': f"The page '{title}' was not found.",
            'user': request.user
        }, status=404)

    # Convert markdown to HTML
    content_html = markdown2.markdown(content)

    # Get edit history from file-based storage
    file_history = load_from_history(title)

    return render(request, 'encyclopedia/entry.html', {
        'title': title,
        'content': content_html,
        'edit_history': file_history[:5] if file_history else [],
        'total_edits': len(file_history) if file_history else 0,
        'user': request.user
    })

def search(request):
    """Search UNIQUE entries (from files)"""
    from .storage import get_all_titles
    query = request.GET.get('q', '').strip()
    all_titles = get_all_titles()

    if not query:
        return render(request, 'encyclopedia/search.html', {
            'query': query,
            'results': [],
            'user': request.user
        })

    # Case-insensitive search
    query_lower = query.lower()
    results = [title for title in all_titles if query_lower in title.lower()]

    return render(request, 'encyclopedia/search.html', {
        'query': query,
        'results': results,
        'user': request.user
    })

@login_required
def edit_page(request, title):
    """Edit existing page"""
    from .storage import get_entry_content, save_entry_locally, sync_with_github
    content = get_entry_content(title)
    
    if content is None:
        messages.info(request, f"Page '{title}' doesn't exist yet. Create it now!")
        return redirect('new_page')

    if request.method == 'POST':
        new_content = request.POST.get('content', '').strip()

        if not new_content:
            messages.error(request, "Content cannot be empty")
            return render(request, 'encyclopedia/edit.html', {
                'title': title,
                'content': content or "",
                'user': request.user
            })

        # Save to file and GitHub
        save_entry_locally(title, new_content)
        github_synced = sync_with_github(title, new_content, request.user.username)
        
        # Save to file-based history
        save_to_history(title, request.user, new_content)
        
        # Show appropriate message
        if github_synced:
            messages.success(request, f"✅ Page '{title}' updated and synced to GitHub!")
        else:
            messages.warning(request, f"⚠️ Page '{title}' saved locally but GitHub sync failed.")
        
        return redirect('entry', title=title)
    
    return render(request, 'encyclopedia/edit.html', {
        'title': title,
        'content': content or "",
        'user': request.user
    })

@login_required
def new_page(request):
    """Create new page"""
    from .storage import get_entry_content, save_entry_locally, sync_with_github
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()

        if not title or not content:
            messages.error(request, "Title and content are required")
            return render(request, 'encyclopedia/new.html', {
                'title': title,
                'content': content,
                'user': request.user
            })

        # Check if page already exists
        existing_content = get_entry_content(title)
        if existing_content is not None:
            messages.info(request, f"Page '{title}' already exists. You can edit it.")
            return redirect('edit_page', title=title)

        # Save to file and GitHub
        save_entry_locally(title, content)
        github_synced = sync_with_github(title, content, request.user.username)
        
        # Save to file-based history
        save_to_history(title, request.user, content)
        
        # Save to database (optional)
        try:
            Entry.objects.create(
                user=request.user, 
                title=title, 
                content=content
            )
        except:
            pass  # Don't crash if database fails
        
        # Show appropriate message
        if github_synced:
            messages.success(request, f"✅ New page '{title}' created and synced to GitHub!")
        else:
            messages.warning(request, f"⚠️ Page '{title}' created locally but GitHub sync failed.")
        
        return redirect('entry', title=title)

    return render(request, 'encyclopedia/new.html', {'user': request.user})

def random_page(request):
    """Redirect to random UNIQUE entry"""
    from .storage import get_all_titles
    titles = get_all_titles()
    
    if not titles:
        return render(request, 'encyclopedia/error.html', {
            'message': "No entries available.",
            'user': request.user
        })

    title = random.choice(titles)
    return redirect('entry', title=title)

def history(request, title):
    """Show edit history from database"""
    entries = Entry.objects.filter(title=title).order_by('-created_at')

    if not entries.exists():
        messages.error(request, f"No history found for '{title}'")
        return redirect('index')

    return render(request, 'encyclopedia/history.html', {
        'title': title,
        'entries': entries,
        'user': request.user
    })

# ============ AI IMAGE VIEWS ============

@login_required
def generate_ai_image(request):
    """Generate AI image from prompt"""
    from .ai_images import generate_craiyon_image
    
    context = {'user': request.user}
    
    if request.method == "POST":
        prompt = request.POST.get("prompt", "").strip()
        
        if not prompt:
            messages.error(request, "Please enter a prompt")
            return redirect('index')
        
        # Rate limiting
        cache_key = f"ai_image_{request.user.id}"
        count = cache.get(cache_key, 0)
        
        if count >= 3:
            context['error'] = "⚠️ Rate limit: 3 images/hour. Please wait."
            return render(request, 'encyclopedia/ai_generated.html', context)
        
        # Generate image
        try:
            start_time = time.time()
            image_url = generate_craiyon_image(prompt)
            generation_time = time.time() - start_time
            
            if image_url:
                # Update rate limit
                cache.set(cache_key, count + 1, 3600)
                
                context.update({
                    'success': True,
                    'image_url': image_url,
                    'prompt': prompt,
                    'generation_time': round(generation_time, 2),
                    'rate_limit_used': count + 1,
                    'rate_limit_max': 3
                })
            else:
                context['error'] = "❌ Failed to generate image. Please try again."
                
        except Exception as e:
            print(f"AI generation error: {e}")
            context['error'] = f"❌ Error: {str(e)}"
    
    return render(request, 'encyclopedia/ai_generated.html', context)
