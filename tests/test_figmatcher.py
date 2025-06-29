#!/usr/bin/env python3
"""
pytest tests for figure_matcher.py
This creates sample images and tests the supports() function.
"""

import tempfile
import json
import pytest
from pathlib import Path
from PIL import Image, ImageDraw
from paper_eval.figmatcher.figure_matcher import supports


@pytest.fixture
def sample_images():
    """Create sample images for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    image_paths = []
    
    # Create a simple chart image
    img1 = Image.new('RGB', (400, 300), color='white')
    draw1 = ImageDraw.Draw(img1)
    
    # Draw a simple bar chart
    draw1.rectangle([50, 200, 100, 250], fill='blue')
    draw1.rectangle([120, 150, 170, 250], fill='red')
    draw1.rectangle([190, 100, 240, 250], fill='green')
    draw1.text((50, 260), "Performance Results", fill='black')
    
    img1_path = temp_dir / "performance_chart.png"
    img1.save(img1_path)
    image_paths.append(img1_path)
    
    # Create a simple diagram
    img2 = Image.new('RGB', (400, 300), color='white')
    draw2 = ImageDraw.Draw(img2)
    
    # Draw a simple flow diagram
    draw2.rectangle([50, 50, 150, 100], fill='lightblue', outline='black')
    draw2.text((70, 70), "Input", fill='black')
    
    draw2.rectangle([250, 50, 350, 100], fill='lightgreen', outline='black')
    draw2.text((270, 70), "Output", fill='black')
    
    # Arrow
    draw2.line([150, 75, 250, 75], fill='black', width=3)
    draw2.polygon([(240, 70), (250, 75), (240, 80)], fill='black')
    
    draw2.text((50, 260), "System Architecture", fill='black')
    
    img2_path = temp_dir / "system_diagram.png"
    img2.save(img2_path)
    image_paths.append(img2_path)
    
    yield image_paths, temp_dir
    
    # Cleanup is automatic with tempfile.mkdtemp()


def test_figmatcher_basic_functionality(sample_images):
    """Test basic functionality with sample data."""
    image_paths, temp_dir = sample_images
    
    # Test case: Simple conclusion with claims
    conclusion = """
    Our experiments demonstrate significant performance improvements. 
    The proposed system architecture shows better efficiency than existing methods.
    Results indicate a 25% increase in processing speed.
    """
    
    result = supports(conclusion, image_paths)
    
    # Should return a dictionary
    assert isinstance(result, dict)
    
    # Should have extracted claims as keys
    assert len(result) > 0
    
    # All values should be boolean
    for claim, supported in result.items():
        assert isinstance(claim, str)
        assert isinstance(supported, bool)
        assert len(claim.strip()) > 0


def test_figmatcher_empty_inputs():
    """Test handling of empty inputs."""
    
    # Empty conclusion
    result1 = supports("", [])
    assert result1 == {}
    
    # Empty images with valid conclusion
    conclusion = "This is a test conclusion."
    result2 = supports(conclusion, [])
    assert result2 == {}
    
    # Empty conclusion with valid images (using dummy paths)
    result3 = supports("", ["dummy_path.png"])
    assert result3 == {}


def test_figmatcher_technical_conclusion():
    """Test with technical conclusion using real image."""
    # Use real image from tests/tmp_images
    image_path = Path(__file__).parent / "tmp_images" / "image_1.png"
    image_paths = [image_path]
    
    conclusion = """
    The neural network architecture achieves state-of-the-art performance on benchmark datasets.
    Training converged after 100 epochs with a final accuracy of 95.2%.
    The attention mechanism significantly improves model interpretability.
    """
    
    print(f"\n=== Figmatcher Technical Conclusion Test ===")
    print(f"Image path: {image_path}")
    print(f"Image exists: {image_path.exists()}")
    print(f"Conclusion: {conclusion.strip()}")
    
    result = supports(conclusion, image_paths)
    
    print(f"\n=== Results ===")
    print(f"Result type: {type(result)}")
    print(f"Number of claims analyzed: {len(result)}")
    if result:
        print(f"\nClaim Analysis:")
        for i, (claim, supported) in enumerate(result.items(), 1):
            status = "✅ SUPPORTED" if supported else "❌ NOT SUPPORTED"
            print(f"{i}. {status}")
            print(f"   Claim: {claim}")
    else:
        print("No claims were analyzed (empty result)")
    
    # Should return a dictionary
    assert isinstance(result, dict)
    
    # All values should be boolean
    for claim, supported in result.items():
        assert isinstance(claim, str)
        assert isinstance(supported, bool)


def test_figmatcher_error_handling():
    """Test error handling with invalid inputs."""
    
    # Non-existent image paths
    result = supports("Test conclusion", ["non_existent_image.png"])
    # Should return empty dict on error (graceful failure)
    assert isinstance(result, dict) 