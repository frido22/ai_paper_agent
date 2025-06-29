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
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TEMPERATURE: float = 0.1
    OPENAI_MAX_TOKENS: int = 2000
    
    # Chunk-based processing settings
    PAGES_PER_CHUNK: int = 10  # Number of pages to process together
    MAX_CHUNK_TEXT_LENGTH: int = 12000  # Maximum text length per chunk
    
    # Component extraction settings
    MAX_TEXT_LENGTH: int = 8000  # Maximum text length to send to OpenAI
    MIN_COMPONENT_LENGTH: int = 10  # Minimum length for a component text
    
    # Relationship extraction settings
    MAX_COMPONENTS_PER_CHUNK: int = 20  # Maximum components to analyze per chunk
    MAX_RELATIONSHIPS_PER_CHUNK: int = 30  # Maximum relationships to extract per chunk
    
    # Context settings
    MAX_CONTEXT_COMPONENTS: int = 10  # Maximum previous components to include in context
    MAX_CONTEXT_RELATIONSHIPS: int = 10  # Maximum previous relationships to include in context
    
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
        
        if cls.OPENAI_TEMPERATURE < 0 or cls.OPENAI_TEMPERATURE > 2:
            errors.append("OPENAI_TEMPERATURE must be between 0 and 2")
        
        if cls.OPENAI_MAX_TOKENS <= 0:
            errors.append("OPENAI_MAX_TOKENS must be positive")
        
        if cls.PAGES_PER_CHUNK <= 0:
            errors.append("PAGES_PER_CHUNK must be positive")
        
        if cls.PAGES_PER_CHUNK > 30:
            errors.append("PAGES_PER_CHUNK should not exceed 30 for optimal performance")
        
        if cls.MAX_CHUNK_TEXT_LENGTH <= 0:
            errors.append("MAX_CHUNK_TEXT_LENGTH must be positive")
        
        if cls.MAX_TEXT_LENGTH <= 0:
            errors.append("MAX_TEXT_LENGTH must be positive")
        
        if cls.MIN_COMPONENT_LENGTH <= 0:
            errors.append("MIN_COMPONENT_LENGTH must be positive")
        
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
            "temperature": cls.OPENAI_TEMPERATURE,
            "max_tokens": cls.OPENAI_MAX_TOKENS
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
            "max_components_per_chunk": cls.MAX_COMPONENTS_PER_CHUNK,
            "max_relationships_per_chunk": cls.MAX_RELATIONSHIPS_PER_CHUNK,
            "max_context_components": cls.MAX_CONTEXT_COMPONENTS,
            "max_context_relationships": cls.MAX_CONTEXT_RELATIONSHIPS
        } 