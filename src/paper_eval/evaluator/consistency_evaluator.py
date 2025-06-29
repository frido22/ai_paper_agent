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

_OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo-0125")

_PROMPT_TEMPLATE = (
    """You are an expert reviewer for scientific articles. On a scale from 0 to 100 "
    "rate how well the CONCLUSION section is fully supported by the RESULTS section. "
    "Consider whether major claims in the conclusion are adequately backed by data "
    "and figures. Return strictly JSON with keys 'score' (int) and 'justification'."""
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

    # naive JSON parse without import json to keep deps minimal
    try:
        import json
        data = json.loads(content)
        return int(data["score"]), str(data["justification"])
    except Exception:
        # fallback if model didn't obey format
        return 0, f"Failed to parse model output: {content[:200]}"
