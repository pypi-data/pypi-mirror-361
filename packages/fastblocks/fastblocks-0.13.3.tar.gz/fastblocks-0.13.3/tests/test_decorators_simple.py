"""Simple decorator tests."""

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

from fastblocks.decorators import cached, cache_control, _wrap_in_middleware


def test_cached_decorator_import():
    """Test that cached decorator can be imported."""
    assert cached is not None
    assert callable(cached)


def test_cache_control_decorator_import():
    """Test that cache_control decorator can be imported."""
    assert cache_control is not None
    assert callable(cache_control)


def test_wrap_in_middleware():
    """Test _wrap_in_middleware function."""
    mock_app = MagicMock()
    mock_middleware = MagicMock()
    
    result = _wrap_in_middleware(mock_app, mock_middleware)
    
    # Should return the middleware
    assert result == mock_middleware


def test_cached_decorator_call():
    """Test cached decorator call."""
    mock_cache = MagicMock()
    
    # Test that it returns a callable
    decorator = cached(cache=mock_cache)
    assert callable(decorator)
    
    # Test that the decorator works
    mock_app = MagicMock()
    result = decorator(mock_app)
    assert result is not None


def test_cache_control_decorator_call():
    """Test cache_control decorator call."""
    # Test that it returns a callable
    decorator = cache_control(max_age=3600)
    assert callable(decorator)
    
    # Test that the decorator works
    mock_app = MagicMock()
    result = decorator(mock_app)
    assert result is not None


def test_cached_decorator_with_rules():
    """Test cached decorator with rules."""
    mock_cache = MagicMock()
    mock_rules = [MagicMock()]
    
    decorator = cached(cache=mock_cache, rules=mock_rules)
    assert callable(decorator)
    
    mock_app = MagicMock()
    result = decorator(mock_app)
    assert result is not None


def test_cache_control_decorator_with_kwargs():
    """Test cache_control decorator with various kwargs."""
    decorator = cache_control(
        max_age=3600,
        private=True,
        no_cache=False
    )
    assert callable(decorator)
    
    mock_app = MagicMock()
    result = decorator(mock_app)
    assert result is not None