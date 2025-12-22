import requests
import base64
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

def generate_craiyon_image_with_timeout(prompt, timeout=25):
    """
    Generate AI image with timeout protection
    Returns image URL or None if timeout/failure
    """
    def _generate():
        try:
            print(f"🔧 Generating AI image for: '{prompt}'")
            
            # Call Craiyon API
            response = requests.post(
                "https://api.craiyon.com/v3",
                json={"prompt": prompt},
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"❌ Craiyon API error: {response.status_code}")
                return None
            
            data = response.json()
            
            if 'images' in data and data['images']:
                image_base64 = data['images'][0]
                
                # Try ImgBB upload if API key exists
                imgbb_api_key = os.environ.get('IMGBB_API_KEY', '')
                if imgbb_api_key:
                    try:
                        imgbb_response = requests.post(
                            "https://api.imgbb.com/1/upload",
                            params={"key": imgbb_api_key},
                            data={"image": image_base64},
                            timeout=10
                        )
                        
                        if imgbb_response.status_code == 200:
                            imgbb_data = imgbb_response.json()
                            if imgbb_data.get("success"):
                                return imgbb_data["data"]["url"]
                    except Exception:
                        pass  # Fallback to base64
                
                # Fallback to base64 data URL
                return f"data:image/png;base64,{image_base64}"
                
        except Exception as e:
            print(f"❌ AI generation error: {e}")
        
        return None
    
    # Run with timeout
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_generate)
            result = future.result(timeout=timeout)
            return result
    except FutureTimeoutError:
        print(f"⏰ AI generation timeout after {timeout} seconds")
        return None
    except Exception as e:
        print(f"💥 Thread error: {e}")
        return None

# Keep original function for compatibility
def generate_craiyon_image(prompt):
    """Wrapper for backward compatibility"""
    return generate_craiyon_image_with_timeout(prompt, timeout=20)
