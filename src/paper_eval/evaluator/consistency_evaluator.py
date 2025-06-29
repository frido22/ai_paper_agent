from __future__ import annotations
"""LLM-based consistency scoring (Person C).
Keeps under 400 LOC by isolating prompt text and using OpenAI chat completions.
"""

import os
from typing import Tuple
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

__all__ = ["score"]

_OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

_PROMPT_TEMPLATE = (
    """You are an expert reviewer for scientific articles. On a scale from 0 to 100, "
    "rate the overall consistency and coherence of this paper. Evaluate how well the "
    "conclusions are supported by the results, how logical the argumentation is, and "
    "how well the different sections connect together. "
    "Give a brief justification on the score you gave."
    "Return strictly JSON with keys 'score' (int) and 'justification'."""
)


def _build_messages(page_data) -> list[dict]:
    # Extract text from all pages
    full_text = "\n".join(page.get("text", "") for page in page_data)
    
    messages = [
        {
            "role": "system",
            "content": _PROMPT_TEMPLATE,
        },
        {
            "role": "user",
            "content": f"PAPER TEXT:\n{full_text}",
        },
    ]
    return messages


def score(page_data) -> Tuple[int, str]:
    """Return (score, justification) by querying the OpenAI chat endpoint."""
    client = OpenAI()
    messages = _build_messages(page_data)
    response = client.chat.completions.create(
        model=_OPENAI_MODEL,
        messages=messages,
        temperature=0.2,
        max_tokens=300,
    )
    content = response.choices[0].message.content.strip()

    # Handle markdown-wrapped JSON responses
    if content.startswith("```json"):
        # Extract JSON from markdown code blocks
        start_idx = content.find("{")
        end_idx = content.rfind("}") + 1
        if start_idx != -1 and end_idx > start_idx:
            content = content[start_idx:end_idx]

    # Parse JSON response
    try:
        import json
        data = json.loads(content)
        return int(data["score"]), str(data["justification"])
    except Exception:
        # fallback if model didn't obey format
        return 0, f"Failed to parse model output: {content[:200]}"
