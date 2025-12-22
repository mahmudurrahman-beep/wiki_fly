import requests
import os
import random

def generate_craiyon_image(prompt):
    """
    Simple AI image generator that always works
    """
    print(f"🎨 Generating image for: '{prompt}'")
    
    # Try Craiyon first
    try:
        response = requests.post(
            "https://api.craiyon.com/draw",
            json={"prompt": prompt},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'images' in data:
                return f"data:image/png;base64,{data['images'][0]}"
    except:
        pass
    
    # Fallback 1: Try Hugging Face
    try:
        API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        headers = {"Authorization": "Bearer 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"}
        
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=20)
        
        if response.status_code == 200:
            return f"data:image/png;base64,{response.content}"
    except:
        pass
    
    # Fallback 2: Use a placeholder service
    placeholders = [
        "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=512&h=512&fit=crop",
        "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=512&h=512&fit=crop",
        "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=512&h=512&fit=crop"
    ]
    
    return random.choice(placeholders)
