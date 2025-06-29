from __future__ import annotations
"""Figure support analysis (Person D).
Uses GPT-4o-mini to check if conclusion claims are backed by images.
"""

import json
import base64
from typing import Dict, List
from pathlib import Path
from openai import OpenAI

from ..utils.config import OPENAI_VISION_MODEL

__all__ = ["supports"]

_PROMPT_TEMPLATE = """You are an expert at analyzing claims and images in research papers.

Your task is to:
1. Extract individual claims from the conclusion
2. Check if each claim is supported by any of the provided images
3. Return a JSON array where each object has:
   - "claim": the specific claim text
   - "supported": true/false

Be strict - only mark as supported if the image clearly provides evidence for the claim.
Return valid JSON only."""


def _encode_image(image_path: str | Path) -> str:
    """Encode image to base64 for OpenAI API."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def _build_messages(conclusion: str, image_paths: List[str | Path]) -> list[dict]:
    """Build messages for OpenAI API with conclusion and images."""
    content = [
        {
            "type": "text",
            "text": f"CONCLUSION:\n{conclusion}\n\nAnalyze if the images support claims in this conclusion."
        }
    ]
    
    # Add each image
    for i, image_path in enumerate(image_paths):
        try:
            base64_image = _encode_image(image_path)
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })
        except Exception as e:
            print(f"Failed to encode image {image_path}: {e}")
    
    messages = [
        {
            "role": "system",
            "content": _PROMPT_TEMPLATE,
        },
        {
            "role": "user",
            "content": content,
        },
    ]
    return messages


def supports(conclusion: str, image_paths: List[str | Path]) -> Dict[str, bool]:
    """Check which conclusion claims are supported by images.
    
    Parameters
    ----------
    conclusion : str
        The conclusion text from the paper
    image_paths : List[str | Path]
        List of paths to images from the paper
        
    Returns
    -------
    Dict[str, bool]
        Mapping of claim text → support flag
    """
    if not conclusion.strip() or not image_paths:
        return {}
    
    client = OpenAI()
    messages = _build_messages(conclusion, image_paths)
    
    try:
        response = client.chat.completions.create(
            model=OPENAI_VISION_MODEL,
            messages=messages,
            temperature=0.1,
            max_tokens=500,
        )
        content = response.choices[0].message.content.strip()
        
        # Handle markdown-wrapped JSON (```json...```)
        if content.startswith('```json'):
            # Extract JSON from markdown code block
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end > start:
                content = content[start:end]
        
        # Parse JSON response
        data = json.loads(content)
        
        # Convert to simple claim -> supported mapping
        support_map = {}
        for item in data:
            if isinstance(item, dict) and "claim" in item and "supported" in item:
                support_map[item["claim"]] = bool(item["supported"])
        
        return support_map
        
    except Exception as e:
        # Fallback: return empty dict on any error
        print(f"Figure matcher error: {e}")
        return {}
