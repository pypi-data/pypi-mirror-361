"""Test caching constants and basic functionality."""

import sys
import types
from unittest.mock import MagicMock

import pytest

# Mock ACB modules before importing
acb_module = types.ModuleType("acb")
acb_depends_module = types.ModuleType("acb.depends")

# Mock depends
mock_depends = MagicMock()
mock_depends.get = MagicMock(return_value=MagicMock())
setattr(acb_depends_module, "depends", mock_depends)

# Register modules
sys.modules["acb"] = acb_module
sys.modules["acb.depends"] = acb_depends_module

from fastblocks.caching import (
    cacheable_methods,
    cacheable_status_codes,
    invalidating_methods,
    CacheDirectives,
    CacheUtils,
)


def test_cacheable_methods():
    """Test cacheable methods constant."""
    assert isinstance(cacheable_methods, frozenset)
    assert "GET" in cacheable_methods
    assert "HEAD" in cacheable_methods
    # OPTIONS may not be in cacheable methods in all implementations


def test_cacheable_status_codes():
    """Test cacheable status codes constant."""
    assert isinstance(cacheable_status_codes, frozenset)
    assert 200 in cacheable_status_codes
    assert 301 in cacheable_status_codes
    assert 404 in cacheable_status_codes


def test_invalidating_methods():
    """Test invalidating methods constant."""
    assert isinstance(invalidating_methods, frozenset)
    assert "POST" in invalidating_methods
    assert "PUT" in invalidating_methods
    assert "DELETE" in invalidating_methods
    assert "PATCH" in invalidating_methods


def test_cache_directives_creation():
    """Test CacheDirectives creation."""
    directives = CacheDirectives()
    
    # Check that it's a dict-like object
    assert isinstance(directives, dict)


def test_cache_utils_creation():
    """Test CacheUtils creation."""
    cache_utils = CacheUtils()
    
    # Check that it has expected attributes
    assert hasattr(cache_utils, '__dict__')
    assert isinstance(cache_utils.__dict__, dict)


def test_cache_directives_with_values():
    """Test CacheDirectives with values."""
    directives = CacheDirectives(
        max_age=3600,
        private=True,
        no_cache=False
    )
    
    # Should have the keys set
    assert directives["max_age"] == 3600
    assert directives["private"] is True
    assert directives["no_cache"] is False


def test_cache_utils_safe_log():
    """Test CacheUtils safe_log method."""
    mock_logger = MagicMock()
    
    # Test that safe_log exists and is callable
    assert hasattr(CacheUtils, 'safe_log')
    assert callable(CacheUtils.safe_log)
    
    # Test calling safe_log
    CacheUtils.safe_log(mock_logger, "info", "test message")


def test_cache_constants_types():
    """Test that cache constants are correct types."""
    # Test types
    assert isinstance(cacheable_methods, frozenset)
    assert isinstance(cacheable_status_codes, frozenset)
    assert isinstance(invalidating_methods, frozenset)
    
    # Test they're not empty
    assert len(cacheable_methods) > 0
    assert len(cacheable_status_codes) > 0
    assert len(invalidating_methods) > 0


def test_cache_directives_immutability():
    """Test that cache constants are immutable."""
    # frozenset should be immutable
    with pytest.raises(AttributeError):
        cacheable_methods.add("NEW_METHOD")
    
    with pytest.raises(AttributeError):
        cacheable_status_codes.add(999)
    
    with pytest.raises(AttributeError):
        invalidating_methods.add("NEW_METHOD")