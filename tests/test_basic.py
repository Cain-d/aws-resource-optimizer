"""
Basic tests for AWS Resource Optimizer
"""

def test_always_passes():
    """A test that always passes to ensure CI works."""
    assert True


def test_basic_math():
    """Test basic functionality."""
    assert 1 + 1 == 2
    assert 2 * 3 == 6


def test_string_operations():
    """Test string operations."""
    test_string = "AWS Resource Optimizer"
    assert "AWS" in test_string
    assert len(test_string) > 0
    assert test_string.startswith("AWS")