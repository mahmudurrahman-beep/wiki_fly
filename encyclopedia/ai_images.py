import requests
import base64
import os
import json

def generate_craiyon_image(prompt):
    """
    Generate AI image using alternative APIs
    Returns the image URL or placeholder if failed
    """
    try:
        print(f"🔧 Generating AI image for: '{prompt}'")
        
        # Try Method 1: Craiyon alternative (DALL-E mini)
        try:
            print("🔄 Trying DALL-E mini API...")
            response = requests.post(
                "https://bf.dallemini.ai/generate",
                json={"prompt": prompt},
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Content-Type': 'application/json'
                },
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'images' in data and data['images']:
                    image_base64 = data['images'][0]
                    print("✅ Got image from DALL-E mini")
                    return process_and_upload_image(image_base64)
        except Exception as e:
            print(f"❌ DALL-E mini failed: {e}")
        
        # Try Method 2: Alternative AI API
        try:
            print("🔄 Trying alternative API...")
            response = requests.post(
                "https://api.picfinder.ai/api/v1/generate",
                json={
                    "prompt": prompt,
                    "width": 512,
                    "height": 512,
                    "style": "digital-art"
                },
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Content-Type': 'application/json'
                },
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'image' in data:
                    image_url = data['image']
                    print(f"✅ Got image from alternative API: {image_url[:50]}...")
                    return image_url
        except Exception as e:
            print(f"❌ Alternative API failed: {e}")
        
        # Method 3: Stable Diffusion API (free tier)
        try:
            print("🔄 Trying Stable Diffusion API...")
            response = requests.post(
                "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1",
                headers={
                    "Authorization": "Bearer hf_your_token_here",  # Free token
                    "User-Agent": "WikiAI/1.0"
                },
                json={"inputs": prompt},
                timeout=25
            )
            
            if response.status_code == 200:
                image_data = response.content
                # Convert to base64
                import base64
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                print("✅ Got image from Stable Diffusion")
                return process_and_upload_image(image_base64)
        except Exception as e:
            print(f"❌ Stable Diffusion failed: {e}")
        
        # Fallback to placeholder
        print("⚠️ All APIs failed, using placeholder")
        return get_placeholder_image(prompt)
        
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return get_placeholder_image(prompt)

def process_and_upload_image(image_base64):
    """Process base64 image and upload to ImgBB"""
    # Upload to ImgBB if API key exists
    imgbb_api_key = os.environ.get('IMGBB_API_KEY', '')
    
    if imgbb_api_key:
        try:
            print("🌐 Uploading to ImgBB...")
            imgbb_response = requests.post(
                "https://api.imgbb.com/1/upload",
                params={"key": imgbb_api_key},
                data={"image": image_base64},
                timeout=15
            )
            
            if imgbb_response.status_code == 200:
                imgbb_data = imgbb_response.json()
                if imgbb_data.get("success"):
                    img_url = imgbb_data["data"]["url"]
                    print(f"✅ ImgBB upload successful: {img_url[:50]}...")
                    return img_url
        except Exception as e:
            print(f"❌ ImgBB upload failed: {e}")
    
    # Fallback to base64 data URL
    print("🔄 Using base64 data URL fallback")
    return f"data:image/png;base64,{image_base64}"

def get_placeholder_image(prompt):
    """Generate placeholder image with prompt text"""
    # Create a simple placeholder with the prompt
    import urllib.parse
    encoded_prompt = urllib.parse.quote(prompt[:30])
    return f"https://placehold.co/512x512/007bff/ffffff?text=AI+Generated&font=montserrat"
