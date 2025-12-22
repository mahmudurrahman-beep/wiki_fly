import requests
import os

def generate_craiyon_image(prompt):
    """Try multiple AI services, falling back if one fails."""
    
    # --- TRY LEONARDO.AI (if API key is set) ---
    leonardo_key = os.environ.get('LEONARDO_API_KEY')
    if leonardo_key:
        try:
            print("🔄 Trying Leonardo.AI...")
            response = requests.post(
                'https://cloud.leonardo.ai/api/rest/v1/generations',
                headers={'Authorization': f'Bearer {leonardo_key}'},
                json={
                    'prompt': prompt,
                    'modelId': 'e316348f-7773-490e-adcd-46757c738eb7', # Example SDXL model
                    'width': 512,
                    'height': 512
                },
                timeout=30
            )
            if response.status_code == 200:
                generation_id = response.json().get('sdGenerationJob', {}).get('generationId')
                # Leonardo requires waiting for generation and fetching the result
                # This is simplified. Full code would need to poll for status.
                if generation_id:
                    # Simplified return - you'd implement polling logic here
                    return f"https://cdn.leonardo.ai/generations/{generation_id}.png"
        except Exception as e:
            print(f"Leonardo.AI attempt failed: {e}")
    
    # --- TRY HUGGING FACE (if token is set) ---
    hf_token = os.environ.get('HF_API_TOKEN')
    if hf_token:
        try:
            print("🔄 Trying Hugging Face...")
            response = requests.post(
                'https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1',
                headers={'Authorization': f'Bearer {hf_token}'},
                json={'inputs': prompt},
                timeout=45
            )
            if response.status_code == 200:
                # Hugging Face returns image bytes. Upload to ImgBB or convert.
                # For simplicity, let's use a base64 data URL:
                import base64
                return f"data:image/png;base64,{base64.b64encode(response.content).decode('utf-8')}"
        except Exception as e:
            print(f"Hugging Face attempt failed: {e}")
    
    # --- FALLBACK TO POLLINATIONS.AI ---
    try:
        clean_prompt = requests.utils.quote(prompt)
        pollinations_url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=512&height=512&model=flux"
        return pollinations_url
    except:
        # Final placeholder fallback
        import urllib.parse
        safe_prompt = urllib.parse.quote(prompt[:30])
        return f"https://placehold.co/512x512/4a6fa5/ffffff?text={safe_prompt}"
