"""
Configuration settings for the argument graph extraction system.

This module contains configuration options for OpenAI API usage,
model parameters, and other system settings.
"""

import os
from typing import Optional
import dotenv

class Config:
    """Configuration class for argument graph extraction."""
    
    dotenv.load_dotenv()
    
    # OpenAI API Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-4o"
    
    # Chunk-based processing settings
    PAGES_PER_CHUNK: int = 35  # Number of pages to process together
    MAX_CHUNK_TEXT_LENGTH: int = 12000  # Maximum text length per chunk
    
    # Validation settings
    ENABLE_VALIDATION: bool = True
    STRICT_MODE: bool = False  # If True, raises errors instead of warnings
    
    @classmethod
    def validate(cls) -> list:
        """
        Validate the configuration and return any issues.
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY environment variable is not set")
        
        if cls.PAGES_PER_CHUNK <= 0:
            errors.append("PAGES_PER_CHUNK must be positive")
        
        if cls.MAX_CHUNK_TEXT_LENGTH <= 0:
            errors.append("MAX_CHUNK_TEXT_LENGTH must be positive")
        
        return errors
    
    @classmethod
    def get_openai_config(cls) -> dict:
        """
        Get OpenAI API configuration as a dictionary.
        
        Returns:
            Dictionary with OpenAI configuration parameters
        """
        return {
            "model": cls.OPENAI_MODEL,
        }
    
    @classmethod
    def set_openai_api_key(cls, api_key: str) -> None:
        """
        Set the OpenAI API key.
        
        Args:
            api_key: The OpenAI API key to set
        """
        cls.OPENAI_API_KEY = api_key
        os.environ["OPENAI_API_KEY"] = api_key
    
    @classmethod
    def get_chunk_config(cls) -> dict:
        """
        Get chunk processing configuration as a dictionary.
        
        Returns:
            Dictionary with chunk processing parameters
        """
        return {
            "pages_per_chunk": cls.PAGES_PER_CHUNK,
            "max_chunk_text_length": cls.MAX_CHUNK_TEXT_LENGTH,
        } 