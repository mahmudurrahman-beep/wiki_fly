# encyclopedia/ai_images.py
import urllib.parse

def generate_craiyon_image(prompt):
    """Generate AI image using Pollinations.ai"""
    try:
        # URL encode the prompt
        clean_prompt = urllib.parse.quote(prompt, safe='')
        
        # Construct Pollinations URL
        pollinations_url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=512&height=512&model=flux"
        
        print(f"✅ Generated URL for '{prompt}': {pollinations_url[:80]}...")
        return pollinations_url
        
    except Exception as e:
        print(f"❌ Error generating image: {e}")
        # Fallback placeholder
        safe_prompt = urllib.parse.quote(prompt[:30])
        return f"https://placehold.co/512x512/4a6fa5/ffffff?text={safe_prompt}"
