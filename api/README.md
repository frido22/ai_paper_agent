# Argument Graph Extraction API

A FastAPI application that extracts argumentative components and relationships from PDF documents using advanced natural language processing.

## Features

- **PDF Upload**: Accept PDF files via HTTP POST requests
- **Automatic Processing**: Integrates with the ingestion pipeline and graph extraction system
- **Comprehensive Analysis**: Extracts multiple types of argumentative components:
  - Claims, Evidence, Conclusions, Counterclaims, Background
  - Methods, Results, Limitations (enhanced types)
- **Rich Relationships**: Identifies various logical relationships:
  - supported_by, contradicted_by, leads_to, elaborates
  - addresses, compares_to, builds_on, motivates, demonstrates
- **Detailed Statistics**: Provides comprehensive analysis statistics
- **JSON Response**: Returns structured JSON with the complete argument graph

## Quick Start

### 1. Install Dependencies

```bash
# From the project root directory
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### 3. Run the API

```bash
cd api
python main.py
```

The API will be available at `http://localhost:8000`

### 4. Test the API

```bash
python test_api.py path/to/your/document.pdf
```

## API Endpoints

### POST `/extract-argument-graph/`

Upload a PDF file and extract the argument graph.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: PDF file in the `file` field

**Response:**
```json
{
  "success": true,
  "document_info": {
    "filename": "document.pdf",
    "total_pages": 10,
    "content_hash": "abc123..."
  },
  "graph_statistics": {
    "total_components": 25,
    "total_relationships": 30,
    "components_by_type": {
      "Claim": 8,
      "Evidence": 12,
      "Conclusion": 3,
      "Method": 2
    },
    "relationships_by_type": {
      "supported_by": 15,
      "leads_to": 8,
      "elaborates": 7
    }
  },
  "argument_graph": {
    "nodes": [...],
    "edges": [...]
  }
}
```

### GET `/health/`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "argument-graph-extraction-api"
}
```

### GET `/`

API information and available endpoints.

## Usage Examples

### Using curl

```bash
curl -X POST "http://localhost:8000/extract-argument-graph/" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@document.pdf"
```

### Using Python requests

```python
import requests

with open('document.pdf', 'rb') as f:
    files = {'file': ('document.pdf', f, 'application/pdf')}
    response = requests.post('http://localhost:8000/extract-argument-graph/', files=files)

if response.status_code == 200:
    result = response.json()
    print(f"Extracted {result['graph_statistics']['total_components']} components")
    print(f"Found {result['graph_statistics']['total_relationships']} relationships")
```

### Using JavaScript/Fetch

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/extract-argument-graph/', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log('Extraction completed:', data);
});
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `PORT`: Port to run the server on (default: 8000)
- `HOST`: Host to bind to (default: 0.0.0.0)

### File Size Limits

- Maximum PDF file size: 50MB
- Supported format: PDF only

## Response Format

### Document Information
- `filename`: Original PDF filename
- `total_pages`: Number of pages in the document
- `content_hash`: Unique hash of the document content

### Graph Statistics
- `total_components`: Total number of argumentative components extracted
- `total_relationships`: Total number of relationships identified
- `components_by_type`: Breakdown of components by type
- `relationships_by_type`: Breakdown of relationships by type

### Argument Graph
- `nodes`: Array of argumentative components with:
  - `id`: Unique component identifier
  - `type`: Component type (Claim, Evidence, etc.)
  - `text`: Extracted text content
  - `page`: Page number where found
- `edges`: Array of relationships with:
  - `source`: Source component ID
  - `target`: Target component ID
  - `relation`: Relationship type
  - `page`: Page where relationship is established

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Successful extraction
- `400`: Invalid request (wrong file type, too large, etc.)
- `500`: Processing error (API key issues, extraction failures, etc.)

Error responses include a descriptive message:

```json
{
  "detail": "File must be a PDF"
}
```

## Development

### Running in Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Testing

```bash
# Test with a specific PDF
python test_api.py path/to/document.pdf

# Test health endpoint
curl http://localhost:8000/health/
```

## Architecture

The API integrates several components:

1. **FastAPI**: Web framework for handling HTTP requests
2. **Ingestion Pipeline**: Processes PDF files and extracts text/tables using PageData objects
3. **Argument Extractor**: Identifies argumentative components and relationships using enhanced prompts
4. **OpenAI Integration**: Uses GPT models for natural language understanding

The API works directly with the ingestion pipeline's native `PageData` format, eliminating the need for data conversion and ensuring optimal performance.

## Troubleshooting

### Common Issues

1. **OpenAI API Key Not Set**
   ```
   Error: OPENAI_API_KEY environment variable is not set
   ```
   Solution: Set the environment variable with your OpenAI API key

2. **File Too Large**
   ```
   Error: File size must be less than 50MB
   ```
   Solution: Use a smaller PDF file or compress the document

3. **Invalid File Type**
   ```
   Error: File must be a PDF
   ```
   Solution: Ensure you're uploading a valid PDF file

4. **Processing Timeout**
   - Large documents may take several minutes to process
   - Consider breaking large documents into smaller sections

### Performance Tips

- Use smaller PDF files for faster processing
- Ensure good internet connection for OpenAI API calls
- Monitor API usage to avoid rate limits

## License

This project is part of the AI Paper Agent system.