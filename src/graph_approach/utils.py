"""
Utility functions for argument graph extraction.

This module provides helper functions for text processing,
validation, and other common operations used in the argument
graph extraction system.
"""

import re
import json
from typing import List, Dict, Any, Optional, Tuple
from .config import Config


def clean_text(text: str) -> str:
    """
    Clean and normalize text for processing.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might interfere with JSON parsing
    text = text.replace('\n', ' ').replace('\r', ' ')
    
    # Trim whitespace
    text = text.strip()
    
    return text


def extract_json_from_response(response_text: str) -> Optional[List[Dict[str, Any]]]:
    """
    Extract JSON array from OpenAI response text.
    
    Args:
        response_text: Raw response text from OpenAI
        
    Returns:
        Parsed JSON array or None if parsing fails
    """
    try:
        # Try to find JSON array in the response
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        
        # Try to parse the entire response as JSON
        return json.loads(response_text)
        
    except (json.JSONDecodeError, AttributeError):
        return None


def validate_component_data(component_data: Dict[str, Any]) -> List[str]:
    """
    Validate component data structure.
    
    Args:
        component_data: Component data to validate
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    required_fields = ['text', 'type']
    for field in required_fields:
        if field not in component_data:
            errors.append(f"Missing required field: {field}")
    
    if 'text' in component_data:
        text = component_data['text']
        if not isinstance(text, str):
            errors.append("'text' must be a string")
    
    if 'type' in component_data:
        valid_types = [
            'Claim', 'Evidence', 'Conclusion', 'Counterclaim', 'Background',
            'Method', 'Result', 'Limitation'
        ]
        if component_data['type'] not in valid_types:
            errors.append(f"Invalid type: {component_data['type']}. Must be one of {valid_types}")
    
    # Validate page number if present
    if 'page' in component_data:
        page = component_data['page']
        if not isinstance(page, int) or page <= 0:
            errors.append("'page' must be a positive integer")
    
    return errors


def validate_relation_data(relation_data: Dict[str, Any]) -> List[str]:
    """
    Validate relationship data structure.
    
    Args:
        relation_data: Relationship data to validate
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    required_fields = ['source', 'target', 'relation']
    for field in required_fields:
        if field not in relation_data:
            errors.append(f"Missing required field: {field}")
    
    if 'relation' in relation_data:
        valid_relations = [
            'supported_by', 'contradicted_by', 'leads_to', 'elaborates',
            'addresses', 'compares_to', 'builds_on', 'motivates', 'demonstrates'
        ]
        if relation_data['relation'] not in valid_relations:
            errors.append(f"Invalid relation: {relation_data['relation']}. Must be one of {valid_relations}")
    
    return errors


def generate_component_id(component_type: str, page_number: int, index: int) -> str:
    """
    Generate a unique component ID.
    
    Args:
        component_type: Type of the component
        page_number: Page number
        index: Index within the page
        
    Returns:
        Unique component ID
    """
    type_prefix = component_type[0].upper()
    return f"P{page_number}-{type_prefix}{index+1}"


def find_text_span(text: str, component_text: str) -> Optional[Tuple[int, int]]:
    """
    Find the exact span of component text within the full text.
    
    Args:
        text: Full text to search in
        component_text: Component text to find
        
    Returns:
        Tuple of (start_index, end_index) or None if not found
    """
    # Clean both texts for comparison
    clean_full = clean_text(text)
    clean_component = clean_text(component_text)
    
    # Try exact match first
    start = clean_full.find(clean_component)
    if start != -1:
        return (start, start + len(clean_component))
    
    # Try fuzzy matching (case insensitive)
    start = clean_full.lower().find(clean_component.lower())
    if start != -1:
        return (start, start + len(clean_component))
    
    # Try matching with some tolerance for whitespace differences
    component_words = clean_component.split()
    full_words = clean_full.split()
    
    for i in range(len(full_words) - len(component_words) + 1):
        if full_words[i:i+len(component_words)] == component_words:
            # Calculate approximate character positions
            start_pos = len(' '.join(full_words[:i])) + (1 if i > 0 else 0)
            end_pos = start_pos + len(clean_component)
            return (start_pos, end_pos)
    
    return None


def merge_overlapping_components(components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merge components that have overlapping text spans.
    
    Args:
        components: List of component dictionaries
        
    Returns:
        List of merged components
    """
    if not components:
        return []
    
    # Sort by text length (longer components first)
    sorted_components = sorted(components, key=lambda x: len(x['text']), reverse=True)
    
    merged = []
    used_spans = set()
    
    for component in sorted_components:
        text = component['text']
        
        # Check if this component overlaps with any already used text
        overlaps = False
        for used_text in used_spans:
            if text in used_text or used_text in text:
                overlaps = True
                break
        
        if not overlaps:
            merged.append(component)
            used_spans.add(text)
    
    return merged


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two text strings.
    
    Args:
        text1: First text string
        text2: Second text string
        
    Returns:
        Similarity score between 0 and 1
    """
    # Simple Jaccard similarity on word sets
    words1 = set(clean_text(text1).lower().split())
    words2 = set(clean_text(text2).lower().split())
    
    if not words1 and not words2:
        return 1.0
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0


def format_prompt_for_components(text: str) -> str:
    """
    Format a prompt for component extraction.
    
    Args:
        text: Text to analyze
        
    Returns:
        Formatted prompt
    """
    return f"""
    Analyze the following text and identify argumentative components. For each component, provide:
    1. The exact text span
    2. The component type (Claim, Evidence, Conclusion, Counterclaim, or Background)
    3. A brief justification for the classification
    
    Text to analyze:
    {truncate_text(text)}
    
    Return your analysis as a JSON array with the following structure:
    [
        {{
            "text": "exact text span",
            "type": "Claim|Evidence|Conclusion|Counterclaim|Background",
            "justification": "brief explanation"
        }}
    ]
    
    Guidelines:
    - Claims: Statements that assert something to be true
    - Evidence: Facts, data, or examples that support claims
    - Conclusions: Final statements that follow from reasoning
    - Counterclaims: Opposing arguments or objections
    - Background: Contextual information that sets the stage
    - Be precise with text spans - use exact quotes
    - Identify the most important argumentative elements
    - Focus on high-quality, meaningful components that contribute to the argument structure
    """


def format_prompt_for_relationships(text: str, components: List[Dict[str, Any]]) -> str:
    """
    Format a prompt for relationship extraction.
    
    Args:
        text: Text to analyze
        components: List of identified components
        
    Returns:
        Formatted prompt
    """
    return f"""
    Analyze the following text and identify logical relationships between the argumentative components.
    
    Text:
    {(text)}
    
    Identified components:
    {json.dumps(components, indent=2)}
    
    For each relationship you identify, provide:
    1. Source component ID
    2. Target component ID  
    3. Relationship type (supported_by, contradicted_by, leads_to, elaborates)
    4. Brief explanation
    
    Return as JSON array:
    [
        {{
            "source": "component_id",
            "target": "component_id", 
            "relation": "supported_by|contradicted_by|leads_to|elaborates",
            "explanation": "brief explanation"
        }}
    ]
    
    Relationship types:
    - supported_by: Evidence that supports a claim
    - contradicted_by: Evidence that contradicts a claim
    - leads_to: Logical progression from one component to another
    - elaborates: One component provides more detail about another
    
    Focus on the most important relationships and avoid creating too many connections.
    """


def format_chunk_prompt_for_components(text: str, context_summary: str = "") -> str:
    """
    Format a prompt for component extraction from chunks.
    
    Args:
        text: Combined text from multiple pages
        context_summary: Summary of previous components for context
        
    Returns:
        Formatted prompt
    """
    return f"""
    Analyze the following text and identify argumentative components. For each component, provide:
    1. The exact text span
    2. The component type (Claim, Evidence, Conclusion, Counterclaim, or Background)
    3. The page number where it appears
    4. A brief justification for the classification
    
    {context_summary}
    
    Text to analyze:
    {(text)}
    
    Return your analysis as a JSON array with the following structure:
    [
        {{
            "text": "exact text span",
            "type": "Claim|Evidence|Conclusion|Counterclaim|Background",
            "page": page_number,
            "justification": "brief explanation"
        }}
    ]
    
    Guidelines:
    - Claims: Statements that assert something to be true
    - Evidence: Facts, data, or examples that support claims
    - Conclusions: Final statements that follow from reasoning
    - Counterclaims: Opposing arguments or objections
    - Background: Contextual information that sets the stage
    - Be precise with text spans - use exact quotes
    - Identify the most important argumentative elements
    - Focus on high-quality, meaningful components that contribute to the argument structure
    """


def format_chunk_prompt_for_relationships(
    text: str, 
    components: List[Dict[str, Any]], 
    context_summary: str = ""
) -> str:
    """
    Format a prompt for relationship extraction from chunks.
    
    Args:
        text: Combined text from multiple pages
        components: List of identified components (existing + new)
        context_summary: Summary of previous components and relationships for context
        
    Returns:
        Formatted prompt
    """
    return f"""
    Analyze the following text and identify logical relationships between the argumentative components.
    
    {context_summary}
    
    Text:
    {(text)}
    
    All components (existing + new):
    {json.dumps(components, indent=2)}
    
    For each relationship you identify, provide:
    1. Source component ID
    2. Target component ID  
    3. Relationship type (supported_by, contradicted_by, leads_to, elaborates)
    4. Brief explanation
    
    Return as JSON array:
    [
        {{
            "source": "component_id",
            "target": "component_id", 
            "relation": "supported_by|contradicted_by|leads_to|elaborates",
            "explanation": "brief explanation"
        }}
    ]
    
    Relationship types:
    - supported_by: Evidence that supports a claim
    - contradicted_by: Evidence that contradicts a claim
    - leads_to: Logical progression from one component to another
    - elaborates: One component provides more detail about another
    
    Focus on:
    1. Relationships between new components in this chunk
    2. Relationships between new components and existing components
    3. The most important and clear relationships
    """


def prepare_context_summary(
    existing_components: List[Dict[str, Any]], 
    existing_relationships: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Prepare a summary of existing components and relationships for context.
    
    Args:
        existing_components: Previously extracted components
        existing_relationships: Previously extracted relationships (optional)
        
    Returns:
        Formatted context summary string
    """
    if not existing_components:
        return "No previous components found."
    
    # Summarize existing components
    component_summary = []
    for comp in existing_components:
        component_summary.append({
            'id': comp['id'],
            'type': comp['type'],
            'text': comp['text'][:100] + "..." if len(comp['text']) > 100 else comp['text'],
            'page': comp['page']
        })
    
    context = f"""
    Previous components found ({len(existing_components)} total):
    {json.dumps(component_summary, indent=2)}
    """
    
    # Add relationship summary if provided
    if existing_relationships:
        relation_summary = []
        for rel in existing_relationships:
            relation_summary.append({
                'source': rel['source'],
                'target': rel['target'],
                'relation': rel['relation'],
                'page': rel['page']
            })
        
        context += f"""
    Previous relationships found ({len(existing_relationships)} total):
    {json.dumps(relation_summary, indent=2)}
    """
    
    return context 