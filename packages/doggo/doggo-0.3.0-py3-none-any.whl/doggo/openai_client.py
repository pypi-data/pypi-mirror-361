"""AI client for Doggo - supports OpenAI and Ollama providers."""

import base64
import io
import json
from pathlib import Path
from typing import List, Dict
from PIL import Image
import openai

from doggo.config import load_config


def get_client():
    """Get configured OpenAI client for any provider."""
    config = load_config()
    api_key = config.get("api_key")
    base_url = config.get("provider_url", "https://api.openai.com/v1")
    
    # For OpenAI, API key is required
    if "openai.com" in base_url and not api_key:
        raise ValueError("OpenAI API key required for OpenAI provider")
    
    return openai.OpenAI(
        base_url=base_url,
        api_key=api_key or "sk-local"  # Dummy key for Ollama
    )


def get_embeddings(text: str) -> List[float]:
    """Generate embedding for text using configured provider."""
    config = load_config()
    client = get_client()
    
    response = client.embeddings.create(
        model=config.get("embedding_model", "text-embedding-3-small"),
        input=text
    )
    
    return response.data[0].embedding


def get_metadata(image_path: Path) -> Dict[str, str]:
    """Generate AI metadata using configured provider."""
    config = load_config()
    client = get_client()
    
    # Load and prepare image
    with Image.open(image_path) as img:
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if too large (OpenAI has size limits)
        max_size = 1024
        if max(img.size) > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Save to bytes for API
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG', quality=85)
        img_bytes.seek(0)
        
        # Encode as base64
        base64_image = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
    
    # Generate metadata with structured output
    response = client.chat.completions.create(
        model=config.get("chat_model", "gpt-4o"),
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Analyze this image and return a JSON object with exactly these three fields:
- "description": A detailed description for search purposes (focus on visual elements, objects, colors, composition)
- "category": A single-word or short phrase category (e.g., "flower", "dog", "landscape")
- "filename": A descriptive filename with 2-8 words, filesystem-safe (use underscores, no special chars)

Return a valid JSON object with these exact field names."""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=200
    )
    
    # Parse JSON response (guaranteed to be valid with structured output)
    content = response.choices[0].message.content
    if content:
        metadata = json.loads(content)
        return {
            "description": metadata.get("description", ""),
            "category": metadata.get("category", "uncategorized"),
            "filename": metadata.get("filename", "image")
        }
    
    # Fallback (should rarely happen with structured output)
    return {
        "description": "",
        "category": "uncategorized", 
        "filename": "image"
    } 