# ai_images.py
import requests
import base64
import os
import time

def generate_craiyon_image(prompt):
    """
    Generate AI image using Craiyon API and upload to ImgBB
    Returns the image URL or None if failed
    """
    try:
        # Step 1: Call Craiyon API
        print(f"Generating image for prompt: {prompt}")
        craiyon_response = requests.post(
            "https://api.craiyon.com/v3",
            json={"prompt": prompt},
            timeout=30
        )
        
        if craiyon_response.status_code != 200:
            print(f"Craiyon API error: {craiyon_response.status_code}")
            return None
        
        data = craiyon_response.json()
        
        # Get the first image (base64)
        if 'images' in data and len(data['images']) > 0:
            image_base64 = data['images'][0]
            
            # Step 2: Upload to ImgBB
            imgbb_api_key = os.environ.get('IMGBB_API_KEY', '')
            if not imgbb_api_key:
                print("IMGBB_API_KEY not set")
                # Fallback: Use base64 data URL
                return f"data:image/png;base64,{image_base64}"
            
            # Upload to ImgBB
            imgbb_response = requests.post(
                "https://api.imgbb.com/1/upload",
                params={"key": imgbb_api_key},
                data={"image": image_base64},
                timeout=30
            )
            
            if imgbb_response.status_code == 200:
                imgbb_data = imgbb_response.json()
                if imgbb_data.get("success"):
                    return imgbb_data["data"]["url"]
                else:
                    print(f"ImgBB upload failed: {imgbb_data}")
            else:
                print(f"ImgBB API error: {imgbb_response.status_code}")
            
            # Fallback to base64
            return f"data:image/png;base64,{image_base64}"
            
    except requests.exceptions.Timeout:
        print("Request timeout")
    except Exception as e:
        print(f"Error in AI image generation: {e}")
    
    return None
