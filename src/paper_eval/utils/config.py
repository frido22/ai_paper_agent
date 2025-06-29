from __future__ import annotations
"""Central config helper.
Loads .env vars and exposes constants.
"""

import os
import time
import functools
from typing import Callable, Any
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo-0125")
OPENAI_VISION_MODEL = os.getenv("OPENAI_VISION_MODEL", "gpt-4o-mini")


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """Decorator to retry OpenAI API calls with exponential backoff for rate limiting."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # Check if it's a rate limit error
                    if hasattr(e, 'status_code') and e.status_code == 429:
                        if attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt)  # Exponential backoff
                            print(f"Rate limit hit, retrying in {delay:.1f} seconds... (attempt {attempt + 1}/{max_retries})")
                            time.sleep(delay)
                            continue
                        else:
                            print(f"Max retries ({max_retries}) exceeded for rate limiting")
                            raise
                    else:
                        # For non-rate-limit errors, raise immediately
                        raise
            return None
        return wrapper
    return decorator
