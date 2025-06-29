"""
Argument Graph Extractor

This module provides functionality to extract argumentative components from paper pages
and build a graph structure representing the logical relationships between them.
"""

import json
import re
from typing import List, Dict, Any, Optional
import openai
from .components import ArgumentComponent, ArgumentRelation, ArgumentGraph
from .config import Config
from .utils import (
    clean_text, extract_json_from_response,
    validate_component_data, validate_relation_data,
    generate_component_id, merge_overlapping_components
)


def extract_argument_graph(pages: List[Any]) -> Dict[str, Any]:
    """
    Extract argumentative components from paper pages and build a graph structure.
    
    Args:
        pages: List of PageData objects from ingestion pipeline, each with:
               - page_number (int)
               - text (str)
               - tables (list)
    
    Returns:
        Dictionary containing:
        - nodes: List of argument component objects
        - edges: List of relationship objects
    """
    # Validate configuration
    config_errors = Config.validate()
    if config_errors:
        raise ValueError(f"Configuration errors: {', '.join(config_errors)}")
    
    # Initialize OpenAI client
    if Config.OPENAI_API_KEY:
        client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    else:
        client = openai.OpenAI()  # Will use environment variable
    
    graph = ArgumentGraph()
    
    # Process pages in chunks for better efficiency and context
    chunk_size = Config.PAGES_PER_CHUNK
    for i in range(0, len(pages), chunk_size):
        chunk_pages = pages[i:i + chunk_size]
        print(f"Processing pages {i+1}-{min(i+chunk_size, len(pages))} of {len(pages)}")
        
        # Extract components and relationships for this chunk
        chunk_components, chunk_relationships = _extract_from_chunk(
            chunk_pages, 
            graph.nodes,  # Pass existing nodes for context
            graph.edges,  # Pass existing relationships for context
            client       # Pass OpenAI client
        )
        
        # Add new components to graph
        for component in chunk_components:
            graph.add_node(component)
        
        # Add new relationships to graph
        for relation in chunk_relationships:
            graph.add_edge(relation)
    
    return graph.to_dict()


def _extract_from_chunk(
    chunk_pages: List[Any], 
    existing_nodes: List[ArgumentComponent], 
    existing_edges: List[ArgumentRelation],
    client: openai.OpenAI
) -> tuple[List[ArgumentComponent], List[ArgumentRelation]]:
    """
    Extract components and relationships from a chunk of pages.
    
    Args:
        chunk_pages: List of PageData objects to process in this chunk
        existing_nodes: Previously extracted components for context
        existing_edges: Previously extracted relationships for context
        client: OpenAI client instance
    
    Returns:
        Tuple of (components, relationships) for this chunk
    """
    # Combine text from all pages in the chunk
    combined_text = _combine_chunk_text(chunk_pages)
    
    # Extract components from the combined text
    components = _extract_components_from_chunk(
        combined_text, 
        chunk_pages, 
        existing_nodes,
        client
    )
    
    # Extract relationships considering existing components
    relationships = _extract_relationships_from_chunk(
        combined_text, 
        chunk_pages, 
        components, 
        existing_nodes, 
        existing_edges,
        client
    )
    
    return components, relationships


def _combine_chunk_text(chunk_pages: List[Any]) -> str:
    """
    Combine text from multiple pages in a chunk.
    
    Args:
        chunk_pages: List of PageData objects in the chunk
    
    Returns:
        Combined text with page separators
    """
    combined = []
    for page in chunk_pages:
        page_num = page.page_number
        text = clean_text(page.text)
        combined.append(f"\n--- PAGE {page_num} ---\n{text}\n")
    
    return "\n".join(combined)


def _extract_components_from_chunk(
    combined_text: str, 
    chunk_pages: List[Any], 
    existing_nodes: List[ArgumentComponent],
    client: openai.OpenAI
) -> List[ArgumentComponent]:
    """
    Extract argumentative components from a chunk of text using OpenAI.
    
    Args:
        combined_text: Combined text from all pages in the chunk
        chunk_pages: List of pages in the chunk
        existing_nodes: Previously extracted components for context
        client: OpenAI client instance
    
    Returns:
        List of ArgumentComponent objects
    """
    
    # Prepare context from existing components
    context_summary = _prepare_context_summary(existing_nodes)
    
    prompt = f"""
    Analyze the following academic text and identify comprehensive argumentative components. Extract complete argumentative units rather than just single sentences.

    {context_summary}
    
    Text to analyze:
    {combined_text}
    
    Return your analysis as a JSON array with the following structure:
    [
        {{
            "text": "complete argumentative text span (can be multiple sentences or paragraphs)",
            "type": "Claim|Evidence|Conclusion|Counterclaim|Background|Method|Result|Limitation",
            "page": page_number,
            "justification": "detailed explanation of why this constitutes the specified component type"
        }}
    ]
    
    IMPORTANT:
    - Only use the following types exactly as written (case-sensitive): Claim, Evidence, Conclusion, Counterclaim, Background, Method, Result, Limitation.
    - Do NOT use all uppercase (e.g., 'EVIDENCE') or all lowercase (e.g., 'evidence').
    - If you are unsure, pick the closest matching type from the list above.
    - Responses with invalid or misspelled types will be rejected.
    
    COMPONENT TYPE GUIDELINES:
    
    CLAIMS: 
    - Main assertions, hypotheses, or propositions that the paper argues for
    - Can include multiple related statements that together form a coherent claim
    - Look for statements that express the paper's main arguments or positions
    - Examples: "Our approach outperforms baseline methods", "This demonstrates that...", "We argue that..."
    
    EVIDENCE:
    - Supporting data, experimental results, citations, examples, or facts
    - Can include entire paragraphs describing experiments, datasets, or findings
    - Look for concrete data, statistics, experimental setups, or empirical observations
    - Examples: "Our experiments show 15% improvement", "The dataset contains 10,000 samples", "Previous work found..."
    
    CONCLUSIONS:
    - Final statements that summarize findings or draw implications
    - Can include multiple sentences that together form a conclusion
    - Look for statements that synthesize results or provide final insights
    - Examples: "This work demonstrates...", "Our results suggest...", "In conclusion..."
    
    COUNTERCLAIMS:
    - Opposing arguments, limitations, or objections that the paper addresses
    - Examples: "However, some argue that...", "A potential limitation is...", "Critics suggest..."
    
    BACKGROUND:
    - Contextual information that sets up the problem or provides necessary foundation
    - Can include literature reviews, problem statements, or domain context
    - Look for information that helps readers understand the research context
    - Examples: "Previous work has shown...", "The problem of...", "In recent years..."
    
    METHOD:
    - Descriptions of approaches, algorithms, procedures, or methodologies
    - Can include entire sections explaining how something is done
    - Look for detailed descriptions of techniques, algorithms, or experimental procedures
    - Examples: "Our algorithm works as follows...", "We employ a three-step process...", "The method consists of..."
    
    RESULT:
    - Specific findings, outcomes, or discoveries from experiments or analysis
    - Can include detailed results with specific numbers, comparisons, or observations
    - Look for concrete outcomes, performance metrics, or empirical findings
    - Examples: "The model achieved 94% accuracy", "We found that...", "Results show..."
    
    LIMITATION:
    - Acknowledged weaknesses, constraints, or areas where the work falls short
    - Can include discussions of what the approach cannot do or where it fails
    - Look for honest assessments of shortcomings or scope limitations
    - Examples: "Our approach has several limitations...", "This method cannot handle...", "A drawback is..."
    
    EXTRACTION GUIDELINES:
    - Extract COMPLETE argumentative units, not just single sentences
    - Include all text that belongs to the same argumentative component
    - Prefer longer, more comprehensive extracts over short fragments
    - Ensure each component is self-contained and meaningful on its own
    - Look for natural paragraph or section boundaries
    - Consider the logical flow and coherence of the extracted text
    - Avoid overlapping or redundant components
    - Focus on the most significant and well-developed argumentative elements
    - Focus on high-quality, meaningful components that contribute to the argument structure
    - Ensure each component has clear justification for its classification
    - Aim to extract at least 15 components
    """
    
    try:
        response = client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert academic paper analyst specializing in argumentative structure extraction. You excel at identifying comprehensive argumentative components that capture complete logical units rather than fragmented sentences. You understand the nuances of academic writing and can distinguish between different types of argumentative elements with high precision."},
                {"role": "user", "content": prompt}
            ]
        )
        
        content = response.choices[0].message.content
        # Extract JSON from response
        components_data = extract_json_from_response(content)
    
        if not components_data:
            print(f"Failed to extract JSON from OpenAI response for chunk")
            return []
        
        # Validate and process components
        valid_components = []
        for i, comp_data in enumerate(components_data):
            # Validate component data
            validation_errors = validate_component_data(comp_data)
            if validation_errors:
                print(f"Validation errors for component {i}: {validation_errors}")
                continue
            
            # Get page number from component data or infer from text
            page_number = comp_data.get('page', _infer_page_number(comp_data['text'], chunk_pages))
            
            # Generate component ID
            component_id = generate_component_id(comp_data['type'], page_number, i)
            
            # Create component object
            component = ArgumentComponent(
                id=component_id,
                type=comp_data['type'],
                text=comp_data['text'],
                page=page_number
            )
            
            valid_components.append(component)
        
        # Merge overlapping components
        component_dicts = [comp.to_dict() for comp in valid_components]
        merged_dicts = merge_overlapping_components(component_dicts)
        
        # Convert back to component objects
        merged_components = []
        for i, comp_dict in enumerate(merged_dicts):
            component = ArgumentComponent(
                id=comp_dict.get('id', generate_component_id(comp_dict['type'], comp_dict['page'], i)),
                type=comp_dict['type'],
                text=comp_dict['text'],
                page=comp_dict['page']
            )
            merged_components.append(component)
        
        return merged_components
        
    except Exception as e:
        print(f"Error extracting components from chunk: {e}")
        return []


def _extract_relationships_from_chunk(
    combined_text: str, 
    chunk_pages: List[Any], 
    chunk_components: List[ArgumentComponent], 
    existing_nodes: List[ArgumentComponent], 
    existing_edges: List[ArgumentRelation],
    client: openai.OpenAI
) -> List[ArgumentRelation]:
    """
    Extract relationships from a chunk, considering existing components and relationships.
    
    Args:
        combined_text: Combined text from all pages in the chunk
        chunk_pages: List of pages in the chunk
        chunk_components: Components found in this chunk
        existing_nodes: Previously extracted components
        existing_edges: Previously extracted relationships
        client: OpenAI client instance
    
    Returns:
        List of ArgumentRelation objects
    """
    if len(chunk_components) < 1:
        return []
    
    # Prepare context from existing components and relationships
    context_summary = _prepare_context_summary(existing_nodes, existing_edges)
    
    # Prepare component data for the prompt
    all_components = existing_nodes + chunk_components
    component_data = [{'id': comp.id, 'type': comp.type, 'text': comp.text, 'page': comp.page} for comp in all_components]
    
    prompt = f"""
    Analyze the following academic text and identify meaningful logical relationships between the argumentative components. Focus on relationships that reveal the paper's argumentative structure and logical flow.

    {context_summary}
    
    Text:
    {combined_text}
    
    All components (existing + new):
    {json.dumps(component_data, indent=2)}
    
    For each meaningful relationship you identify, provide:
    1. Source component ID
    2. Target component ID  
    3. Relationship type (see detailed types below)
    4. Detailed explanation of the relationship
    
    Return as JSON array:
    [
        {{
            "source": "component_id",
            "target": "component_id", 
            "relation": "relationship_type",
            "explanation": "detailed explanation of how these components are logically connected"
        }}
    ]
    
    IMPORTANT:
    - Only use the following relationship types exactly as written (case-sensitive): supported_by, contradicted_by, leads_to, elaborates, addresses, compares_to, builds_on, motivates, demonstrates.
    - Do NOT use all uppercase (e.g., 'SUPPORTED_BY') or all lowercase (e.g., 'supported_by').
    - If you are unsure, pick the closest matching type from the list above.
    - Responses with invalid or misspelled relationship types will be rejected.
    
    RELATIONSHIP TYPES:
    
    supported_by:
    - Evidence, data, or examples that directly support a claim
    - Experimental results that validate a hypothesis
    - Citations or references that back up an assertion
    - Examples: "Our claim that X is better is supported_by the experimental results showing 15% improvement"
    
    contradicted_by:
    - Evidence or arguments that challenge or contradict a claim
    - Counterexamples that undermine an assertion
    - Limitations that weaken a position
    - Examples: "The claim that X always works is contradicted_by cases where it fails"
    
    leads_to:
    - Logical progression from one component to another
    - Causal relationships where one component naturally follows from another
    - Sequential reasoning steps in an argument
    - Examples: "The problem statement leads_to the proposed solution", "Background information leads_to the main claim"
    
    elaborates:
    - One component provides more detail, explanation, or context for another
    - Methodological details that expand on a claim
    - Extended discussion that builds upon a previous point
    - Examples: "The main claim is elaborated_by detailed experimental methodology"
    
    addresses:
    - One component directly responds to or deals with issues raised in another
    - Solutions that address problems or limitations
    - Responses to counterarguments or objections
    - Examples: "The limitation is addressed_by the proposed improvement"
    
    compares_to:
    - One component is compared or contrasted with another
    - Evaluations that compare different approaches or results
    - Benchmarking or competitive analysis
    - Examples: "Our method is compared_to baseline approaches"
    
    builds_on:
    - One component extends or improves upon another
    - Incremental advances that build on previous work
    - Enhancements or refinements of earlier ideas
    - Examples: "The improved algorithm builds_on the original approach"
    
    motivates:
    - One component provides motivation or justification for another
    - Problem statements that motivate solutions
    - Background that motivates the research direction
    - Examples: "The problem description motivates the proposed solution"
    
    demonstrates:
    - One component shows or proves the validity of another
    - Results that demonstrate the effectiveness of a method
    - Examples that illustrate a concept
    - Examples: "The experimental results demonstrate the effectiveness of our approach"
    
    RELATIONSHIP EXTRACTION GUIDELINES:
    
    Focus on relationships that:
    1. Reveal the paper's logical structure and argumentative flow
    2. Show how different components work together to build the argument
    3. Highlight the most important connections between ideas
    4. Demonstrate the paper's contribution and reasoning process
    
    Prioritize relationships that:
    - Connect components across different types (e.g., claim-evidence, problem-solution)
    - Show the paper's main argumentative threads
    - Link new components to existing ones for continuity
    - Reveal the paper's unique contributions or insights
    
    Avoid creating relationships that:
    - Are too obvious or trivial
    - Don't add meaningful insight to the argument structure
    - Create circular or redundant connections
    - Connect components that are only superficially related
    
    Quality over quantity:
    - Aim to extract at least 10 relationships or however many are meaningful
    - Focus on high-quality, non-trivial relationships that enhance understanding
    - Focus on high-quality, meaningful relationships
    - Each relationship should provide clear insight into the paper's logic
    - Ensure relationships are well-justified and specific
    - Prefer relationships that span different component types
    """
    
    try:
        response = client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert in academic argument analysis and logical relationship identification. You excel at uncovering the deep logical connections between argumentative components, revealing how academic papers build coherent arguments through various types of relationships. You focus on meaningful, non-trivial connections that illuminate the paper's reasoning structure."},
                {"role": "user", "content": prompt}
            ]
        )
        
        content = response.choices[0].message.content
        
        # Extract JSON from response
        relations_data = extract_json_from_response(content)
        if not relations_data:
            print(f"Failed to extract JSON from OpenAI response for relationships in chunk")
            return []
        
        # Validate and process relationships
        valid_relations = []
        for rel_data in relations_data:
            # Validate relationship data
            validation_errors = validate_relation_data(rel_data)
            if validation_errors:
                print(f"Validation errors for relationship: {validation_errors}")
                continue
            
            # Find the page where this relationship is most clearly established
            source_page = _find_component_page(rel_data['source'], all_components)
            target_page = _find_component_page(rel_data['target'], all_components)
            relation_page = max(source_page, target_page)  # Use the later page
            
            # Create relationship object
            relation = ArgumentRelation(
                source=rel_data['source'],
                target=rel_data['target'],
                relation=rel_data['relation'],
                page=relation_page
            )
            valid_relations.append(relation)
        
        return valid_relations
        
    except Exception as e:
        print(f"Error extracting relationships from chunk: {e}")
        return []


def _prepare_context_summary(
    existing_nodes: List[ArgumentComponent], 
    existing_edges: Optional[List[ArgumentRelation]] = None
) -> str:
    """
    Prepare a summary of existing components and relationships for context.
    
    Args:
        existing_nodes: Previously extracted components
        existing_edges: Previously extracted relationships (optional)
    
    Returns:
        Formatted context summary string
    """
    if not existing_nodes:
        return "No previous components found."
    
    # Summarize existing components
    component_summary = []
    for node in existing_nodes:  # Show last 10 components for context
        component_summary.append({
            'id': node.id,
            'type': node.type,
            'text': node.text[:100] + "..." if len(node.text) > 100 else node.text,
            'page': node.page
        })
    
    context = f"""
    Previous components found ({len(existing_nodes)} total):
    {json.dumps(component_summary, indent=2)}
    """
    
    # Add relationship summary if provided
    if existing_edges:
        relation_summary = []
        for edge in existing_edges:  # Show last 10 relationships for context
            relation_summary.append({
                'source': edge.source,
                'target': edge.target,
                'relation': edge.relation,
                'page': edge.page
            })
        
        context += f"""
    Previous relationships found ({len(existing_edges)} total):
    {json.dumps(relation_summary, indent=2)}
    """
    
    return context


def _infer_page_number(text: str, chunk_pages: List[Any]) -> int:
    """
    Infer the page number for a component based on its text content.
    
    Args:
        text: Component text
        chunk_pages: List of pages in the chunk
    
    Returns:
        Inferred page number
    """
    # Try to find which page contains this text
    for page in chunk_pages:
        if text in page.text:
            return page.page_number
    
    # If not found, return the first page number in the chunk
    return chunk_pages[0].page_number


def _find_component_page(component_id: str, all_components: List[ArgumentComponent]) -> int:
    """
    Find the page number for a component by its ID.
    
    Args:
        component_id: Component ID to search for
        all_components: List of all components
    
    Returns:
        Page number of the component
    """
    for component in all_components:
        if component.id == component_id:
            return component.page
    
    # Default to page 1 if not found
    return 1