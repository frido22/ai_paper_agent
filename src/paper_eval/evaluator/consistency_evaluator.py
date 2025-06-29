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
    """You are an expert reviewer for scientific articles. On a scale from 0 to 100 "
    "rate how well the CONCLUSION section is fully supported by the RESULTS section. "
    "Give a brief justification on the score you gave."
    "Return strictly JSON with keys 'score' (int) and 'justification'."""
)


def _build_messages(results: str, conclusion: str) -> list[dict]:
    messages = [
        {
            "role": "system",
            "content": _PROMPT_TEMPLATE,
        },
        {
            "role": "user",
            "content": f"RESULTS:\n{results}\n\nCONCLUSION:\n{conclusion}",
        },
    ]
    return messages


def score(results: str, conclusion: str) -> Tuple[int, str]:
    """Return (score, justification) by querying the OpenAI chat endpoint."""
    client = OpenAI()
    messages = _build_messages(results, conclusion)
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
