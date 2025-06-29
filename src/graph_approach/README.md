# Argument Graph Extraction System

This module provides functionality to extract argumentative components from academic papers and build a graph structure representing the logical relationships between them.

## Overview

The argument graph extraction system analyzes paper pages to identify:
- **Claims**: Statements that assert something to be true
- **Evidence**: Facts, data, or examples that support claims
- **Conclusions**: Final statements that follow from reasoning
- **Counterclaims**: Opposing arguments or objections
- **Background**: Contextual information that sets the stage

It then identifies logical relationships between these components:
- **supported_by**: Evidence that supports a claim
- **contradicted_by**: Evidence that contradicts a claim
- **leads_to**: Logical progression from one component to another
- **elaborates**: One component provides more detail about another

## Key Features

### 🚀 **Chunk-Based Processing**
- **Efficient Processing**: Processes 2-3 pages per API call instead of page-by-page
- **Context Awareness**: Passes previous components and relationships for better analysis
- **Reduced API Costs**: Significantly fewer API calls for large papers
- **Better Accuracy**: More informed decisions with full context

### 🧠 **Intelligent Analysis**
- **Cross-Page Relationships**: Automatically identifies relationships across page boundaries
- **Context Preservation**: Maintains awareness of previously extracted components
- **Adaptive Processing**: Adjusts analysis based on existing graph structure

## Installation

1. Install the required dependencies:
```bash
pip install openai
```

2. Set your OpenAI API key:
```bash
export OPENAI_API_KEY='py-key-here'
```

## Usage

### Basic Usage

```python
from src.graph_approach.argument_extractor import extract_argument_graph

# Define your pages data
pages = [
    {
        "page_number": 1,
        "text": "Your raw text of the paper's page 1...",
        "tables": [],
        "text_stats": {"word_count": 100, "char_count": 500, "line_count": 10, "table_count": 0}
    },
    # ... more pages
]

# Extract the argument graph
graph_data = extract_argument_graph(pages)

# The result contains nodes and edges
print(f"Found {len(graph_data['nodes'])} components")
print(f"Found {len(graph_data['edges'])} relationships")
```

### Example Output

```python
{
    "nodes": [
        {
            "id": "P1-C1",
            "type": "Claim",
            "text": "Machine learning is effective for image recognition",
            "page": 1
        },
        {
            "id": "P1-E1",
            "type": "Evidence",
            "text": "Our experiments show 95% accuracy on benchmark datasets",
            "page": 1
        }
    ],
    "edges": [
        {
            "source": "P1-C1",
            "target": "P1-E1",
            "relation": "supported_by",
            "page": 1
        }
    ]
}
```

## Configuration

You can customize the behavior by modifying the `Config` class in `config.py`:

```python
from src.graph_approach.config import Config

# Set custom OpenAI model
Config.OPENAI_MODEL = "gpt-4"

# Adjust chunk processing
Config.PAGES_PER_CHUNK = 3  # Process 3 pages together
Config.MAX_CHUNK_TEXT_LENGTH = 12000  # Maximum text per chunk

# Adjust temperature for more/less creative responses
Config.OPENAI_TEMPERATURE = 0.2

# Set maximum tokens for responses
Config.OPENAI_MAX_TOKENS = 3000
```

### Chunk Processing Configuration

```python
# Get chunk processing settings
chunk_config = Config.get_chunk_config()
print(chunk_config)
# Output:
# {
#     'pages_per_chunk': 3,
#     'max_chunk_text_length': 12000,
#     'max_components_per_chunk': 20,
#     'max_relationships_per_chunk': 30,
#     'max_context_components': 10,
#     'max_context_relationships': 10
# }
```

## Components

### Core Classes

- **`ArgumentComponent`**: Represents an argumentative component (claim, evidence, etc.)
- **`ArgumentRelation`**: Represents a logical relationship between components
- **`ArgumentGraph`**: Container for components and relationships with utility methods

### Main Functions

- **`extract_argument_graph(pages)`**: Main function that processes pages and returns graph data
- **`_extract_from_chunk(chunk_pages, existing_nodes, existing_edges)`**: Processes a chunk of pages with context
- **`_extract_components_from_chunk(text, chunk_pages, existing_nodes)`**: Extracts components from chunk text
- **`_extract_relationships_from_chunk(text, chunk_pages, components, existing_nodes, existing_edges)`**: Extracts relationships with context

### Utility Functions

- **`clean_text(text)`**: Cleans and normalizes text
- **`truncate_chunk_text(text)`**: Truncates text for chunk processing
- **`extract_json_from_response(response_text)`**: Extracts JSON from OpenAI responses
- **`validate_component_data(component_data)`**: Validates component data structure
- **`generate_component_id(component_type, page_number, index)`**: Generates unique component IDs
- **`prepare_context_summary(existing_components, existing_relationships)`**: Prepares context for LLM

## Input Format

Each page should be a dictionary with the following structure:

```python
{
    "page_number": int,           # Page number (1-based)
    "text": str,                  # Raw text content of the page
    "tables": list,               # List of tables (optional)
    "text_stats": dict            # Text statistics (optional)
}
```

## Output Format

The function returns a dictionary with two main keys:

```python
{
    "nodes": [                    # List of argumentative components
        {
            "id": str,            # Unique identifier (e.g., "P1-C1")
            "type": str,          # Component type
            "text": str,          # Exact text span
            "page": int           # Page number
        }
    ],
    "edges": [                    # List of relationships
        {
            "source": str,        # Source component ID
            "target": str,        # Target component ID
            "relation": str,      # Relationship type
            "page": int           # Page where relationship is established
        }
    ]
}
```

## Component Types

- **Claim**: Statements that assert something to be true
- **Evidence**: Facts, data, or examples that support claims
- **Conclusion**: Final statements that follow from reasoning
- **Counterclaim**: Opposing arguments or objections
- **Background**: Contextual information that sets the stage

## Relationship Types

- **supported_by**: Evidence that supports a claim
- **contradicted_by**: Evidence that contradicts a claim
- **leads_to**: Logical progression from one component to another
- **elaborates**: One component provides more detail about another

## Chunk-Based Processing Benefits

### Efficiency Improvements

| Paper Size | Old Approach | New Approach | API Call Reduction |
|------------|--------------|--------------|-------------------|
| 3 pages    | 6 calls      | 1 call       | 83% reduction     |
| 6 pages    | 12 calls     | 2 calls      | 83% reduction     |
| 10 pages   | 20 calls     | 4 calls      | 80% reduction     |
| 15 pages   | 30 calls     | 5 calls      | 83% reduction     |

### Quality Improvements

1. **Better Context**: Each chunk has access to previously extracted components
2. **Cross-Page Relationships**: Automatically identifies relationships across page boundaries
3. **Consistent Analysis**: Maintains consistency across the entire paper
4. **Reduced Redundancy**: Avoids re-analyzing similar content

## Error Handling

The system includes comprehensive error handling:
- **Configuration validation**: Checks for valid API keys and settings
- **Input data validation**: Validates page structure and content
- **OpenAI API error handling**: Robust error handling for API calls
- **JSON response parsing**: Handles malformed responses gracefully
- **Graph structure validation**: Checks for orphaned edges and other issues

## Testing

Run the test suite:
```bash
python -m unittest src.graph_approach.test_extractor
```

## Example Usage Script

Run the example script to see the system in action:
```bash
python -m src.graph_approach.example_usage
```

## Performance Considerations

### Chunk Processing
- **Optimal Chunk Size**: 2-3 pages per chunk provides best balance of efficiency and accuracy
- **Text Length Limits**: Automatic truncation to fit within OpenAI's token limits
- **Context Management**: Intelligent context summarization to stay within limits

### API Cost Optimization
- **Reduced Calls**: Chunk processing significantly reduces API calls
- **Efficient Prompts**: Optimized prompts to maximize information extraction
- **Smart Truncation**: Intelligent text truncation to minimize token usage

## Limitations

- Requires OpenAI API access and credits
- Text length is limited by OpenAI API constraints
- Analysis quality depends on the clarity of the input text
- Chunk size should be adjusted based on paper complexity

## Troubleshooting

### Common Issues

1. **API Key Error**: Ensure your OpenAI API key is set correctly
2. **Rate Limiting**: The system includes delays between API calls
3. **Text Too Long**: Text is automatically truncated to fit API limits
4. **No Components Found**: Check that your text contains clear argumentative elements

### Debug Mode

Enable debug output by setting the log level:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Configuration Issues

Check your configuration:
```python
from src.graph_approach.config import Config
errors = Config.validate()
if errors:
    print("Configuration errors:", errors)
```

## Contributing

When contributing to this module:

1. Follow the existing code structure
2. Add tests for new functionality
3. Update documentation for any API changes
4. Ensure all tests pass before submitting

## License

This module is part of the larger AI Paper Agent project and follows the same licensing terms. 