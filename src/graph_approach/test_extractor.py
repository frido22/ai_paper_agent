"""
Test module for argument graph extraction.

This module contains unit tests for the argument graph extraction system.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
from typing import List, Dict, Any

from .argument_extractor import extract_argument_graph
from .components import ArgumentComponent, ArgumentRelation, ArgumentGraph
from .config import Config


class TestArgumentGraphExtraction(unittest.TestCase):
    """Test cases for argument graph extraction functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_pages = [
            {
                "page_number": 1,
                "text": "This paper argues that machine learning is effective. We present evidence from experiments showing 85% accuracy. Our conclusion is that ML works well.",
                "tables": [],
                "text_stats": {"word_count": 25, "char_count": 150, "line_count": 3, "table_count": 0}
            },
            {
                "page_number": 2,
                "text": "However, some researchers disagree with our findings. They claim that traditional methods are better. Our additional experiments refute this claim.",
                "tables": [],
                "text_stats": {"word_count": 20, "char_count": 120, "line_count": 2, "table_count": 0}
            }
        ]
    
    @patch('openai.ChatCompletion.create')
    def test_extract_argument_graph_success(self, mock_openai):
        """Test successful argument graph extraction."""
        # Mock OpenAI responses
        mock_openai.return_value.choices[0].message.content = json.dumps([
            {
                "text": "This paper argues that machine learning is effective",
                "type": "Claim",
                "justification": "This is a statement asserting something to be true"
            },
            {
                "text": "We present evidence from experiments showing 85% accuracy",
                "type": "Evidence",
                "justification": "This provides factual support for the claim"
            }
        ])
        
        # Mock relationship extraction
        mock_openai.return_value.choices[0].message.content = json.dumps([
            {
                "source": "P1-C1",
                "target": "P1-E1",
                "relation": "supported_by",
                "explanation": "Evidence supports the claim"
            }
        ])
        
        # Set up API key
        Config.OPENAI_API_KEY = "test-key"
        
        try:
            result = extract_argument_graph(self.sample_pages)
            
            # Verify structure
            self.assertIn('nodes', result)
            self.assertIn('edges', result)
            self.assertIsInstance(result['nodes'], list)
            self.assertIsInstance(result['edges'], list)
            
        except Exception as e:
            self.fail(f"extract_argument_graph raised an exception: {e}")
    
    def test_argument_component_creation(self):
        """Test ArgumentComponent creation and serialization."""
        component = ArgumentComponent(
            id="P1-C1",
            type="Claim",
            text="This is a test claim",
            page=1
        )
        
        # Test to_dict method
        component_dict = component.to_dict()
        self.assertEqual(component_dict['id'], "P1-C1")
        self.assertEqual(component_dict['type'], "Claim")
        self.assertEqual(component_dict['text'], "This is a test claim")
        self.assertEqual(component_dict['page'], 1)
    
    def test_argument_relation_creation(self):
        """Test ArgumentRelation creation and serialization."""
        relation = ArgumentRelation(
            source="P1-C1",
            target="P1-E1",
            relation="supported_by",
            page=1
        )
        
        # Test to_dict method
        relation_dict = relation.to_dict()
        self.assertEqual(relation_dict['source'], "P1-C1")
        self.assertEqual(relation_dict['target'], "P1-E1")
        self.assertEqual(relation_dict['relation'], "supported_by")
        self.assertEqual(relation_dict['page'], 1)
    
    def test_argument_graph_operations(self):
        """Test ArgumentGraph operations."""
        graph = ArgumentGraph()
        
        # Test adding nodes
        component1 = ArgumentComponent("P1-C1", "Claim", "Test claim", 1)
        component2 = ArgumentComponent("P1-E1", "Evidence", "Test evidence", 1)
        
        graph.add_node(component1)
        graph.add_node(component2)
        
        self.assertEqual(len(graph.nodes), 2)
        
        # Test adding edges
        relation = ArgumentRelation("P1-C1", "P1-E1", "supported_by", 1)
        graph.add_edge(relation)
        
        self.assertEqual(len(graph.edges), 1)
        
        # Test to_dict method
        graph_dict = graph.to_dict()
        self.assertIn('nodes', graph_dict)
        self.assertIn('edges', graph_dict)
        self.assertEqual(len(graph_dict['nodes']), 2)
        self.assertEqual(len(graph_dict['edges']), 1)
    
    def test_argument_graph_validation(self):
        """Test ArgumentGraph validation."""
        graph = ArgumentGraph()
        
        # Add a node
        component = ArgumentComponent("P1-C1", "Claim", "Test claim", 1)
        graph.add_node(component)
        
        # Add an edge with non-existent source
        relation = ArgumentRelation("P1-C2", "P1-C1", "supported_by", 1)
        graph.add_edge(relation)
        
        # Validation should catch the orphaned edge
        errors = graph.validate()
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("does not exist" in error for error in errors))
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Test with valid configuration
        Config.OPENAI_API_KEY = "test-key"
        Config.OPENAI_TEMPERATURE = 0.1
        Config.OPENAI_MAX_TOKENS = 1000
        
        errors = Config.validate()
        self.assertEqual(len(errors), 0)
        
        # Test with invalid temperature
        Config.OPENAI_TEMPERATURE = 3.0
        errors = Config.validate()
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("temperature" in error.lower() for error in errors))
    
    def test_empty_pages_input(self):
        """Test handling of empty pages input."""
        empty_pages = []
        
        with self.assertRaises(ValueError):
            extract_argument_graph(empty_pages)
    
    def test_invalid_page_structure(self):
        """Test handling of invalid page structure."""
        invalid_pages = [
            {
                "page_number": 1,
                # Missing 'text' field
                "tables": [],
                "text_stats": {}
            }
        ]
        
        with self.assertRaises(Exception):
            extract_argument_graph(invalid_pages)


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        from .utils import clean_text
        
        dirty_text = "  This   is\na\ttest\n\n  text  "
        cleaned = clean_text(dirty_text)
        self.assertEqual(cleaned, "This is a test text")
    
    def test_generate_component_id(self):
        """Test component ID generation."""
        from .utils import generate_component_id
        
        id1 = generate_component_id("Claim", 1, 0)
        self.assertEqual(id1, "P1-C1")
        
        id2 = generate_component_id("Evidence", 2, 5)
        self.assertEqual(id2, "P2-E6")
    
    def test_validate_component_data(self):
        """Test component data validation."""
        from .utils import validate_component_data
        
        # Valid component
        valid_component = {
            "text": "This is a valid claim with sufficient length",
            "type": "Claim"
        }
        errors = validate_component_data(valid_component)
        self.assertEqual(len(errors), 0)
        
        # Invalid component (missing text)
        invalid_component = {
            "type": "Claim"
        }
        errors = validate_component_data(invalid_component)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("Missing required field" in error for error in errors))


if __name__ == '__main__':
    unittest.main() 