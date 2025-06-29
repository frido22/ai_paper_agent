"""
FastAPI application for argument graph extraction from PDF files.

This API provides an endpoint to upload PDF files and receive argument graphs
extracted from the document content.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
import json

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.graph_approach.argument_extractor import extract_argument_graph
from src.ingestion.ingest import run_pipeline
from src.ingestion.core.file_object import FileObject
from src.paper_eval.pipeline.run_pipeline import _process

# Initialize FastAPI app
app = FastAPI(
    title="Argument Graph Extraction API",
    description="API for extracting argumentative components and relationships from PDF documents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def validate_pdf_file(file: UploadFile) -> None:
    """
    Validate that the uploaded file is a PDF.
    
    Args:
        file: The uploaded file to validate
        
    Raises:
        HTTPException: If the file is not a valid PDF
    """
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    if file.size and file.size > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 50MB")

def process_pdf_to_json(pdf_path: Path) -> Dict[str, Any]:
    """
    Process a PDF file through ingestion and return the results as a JSON object.
    """
    file_objects = run_pipeline(force_reprocess=True, file_path=pdf_path)
    return file_objects[0]

def process_pdf_to_graph(file_obj: FileObject) -> Dict[str, Any]:
    """
    Process a PDF file through ingestion and graph extraction.
    
    Args:
        file_obj: FileObject containing the processed PDF data
        
    Returns:
        Dictionary containing the argument graph and metadata
    """
    try:
        # Extract pages from FileObject
        pages = file_obj.pages  # Pass PageData objects directly, not as dictionaries
        
        # Extract argument graph
        graph_result = extract_argument_graph(pages)
        
        # Prepare response
        response = {
            "success": True,
            "document_info": {     
                "total_pages": len(pages),
            },
            "graph_statistics": {
                "total_components": len(graph_result["nodes"]),
                "total_relationships": len(graph_result["edges"]),
                "components_by_type": {},
                "relationships_by_type": {}
            },
            "argument_graph": graph_result
        }
        
        # Calculate statistics
        for node in graph_result["nodes"]:
            comp_type = node["type"]
            response["graph_statistics"]["components_by_type"][comp_type] = \
                response["graph_statistics"]["components_by_type"].get(comp_type, 0) + 1
        
        for edge in graph_result["edges"]:
            rel_type = edge["relation"]
            response["graph_statistics"]["relationships_by_type"][rel_type] = \
                response["graph_statistics"]["relationships_by_type"].get(rel_type, 0) + 1
        
        return response
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "argument_graph": None
        }


@app.post("/extract-results/")
async def extract_argument_graph_endpoint(file: UploadFile = File(...)) -> JSONResponse:
    """
    Extract argument graph from uploaded PDF file.
    
    Args:
        file: PDF file to process
        
    Returns:
        JSON response containing the argument graph and metadata
    """
    # Validate the uploaded file
    validate_pdf_file(file)
    
    # Create temporary directory for processing
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Save uploaded file
        pdf_path = temp_dir / file.filename
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_obj = process_pdf_to_json(pdf_path)
        print(file_obj)
        # Process the PDF
        # Construct path to processed pages.json file
        pages_json_path = Path("data/processed") / file_obj.content_hash / "pages.json"
        score_result = _process(pages_json_path)
        print(score_result)
        graph_result = process_pdf_to_graph(file_obj)
        
        if not graph_result["success"]:
            raise HTTPException(status_code=500, detail=graph_result["error"])
        
        # Include score and justification in the response
        response = graph_result.copy()
        response["evaluation"] = {
            "score": score_result.get("score"),
            "justification": score_result.get("justification")
        }

        return JSONResponse(content=response, status_code=200)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle other exceptions
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    finally:
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


@app.get("/health/")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return {"status": "healthy", "service": "argument-graph-extraction-api"}


@app.get("/")
async def root() -> Dict[str, str]:
    """
    Root endpoint with API information.
    
    Returns:
        API information
    """
    return {
        "message": "Argument Graph Extraction API",
        "version": "1.0.0",
        "endpoints": {
            "extract_graph": "/extract-argument-graph/",
            "health": "/health/",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable not set.")
        print("Please set your OpenAI API key to use the extraction functionality.")
    
    # Run the FastAPI application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 