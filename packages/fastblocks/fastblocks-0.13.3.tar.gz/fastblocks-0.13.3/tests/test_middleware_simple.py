"""Simple middleware tests to boost coverage."""

import sys
import types
from unittest.mock import MagicMock

import pytest

# Mock ACB modules before importing
acb_module = types.ModuleType("acb")
acb_depends_module = types.ModuleType("acb.depends")

# Mock depends
mock_depends = MagicMock()
mock_depends.get = MagicMock()
acb_depends_module.depends = mock_depends

# Register modules
sys.modules["acb"] = acb_module
sys.modules["acb.depends"] = acb_depends_module

from fastblocks.middleware import (
    MiddlewarePosition,
    MiddlewareUtils,
    get_middleware_positions,
)


class TestMiddlewareUtilsSimple:
    def test_get_request(self):
        """Test MiddlewareUtils.get_request method."""
        # Set a test scope
        test_scope = {"type": "http", "method": "GET"}
        MiddlewareUtils.set_request(test_scope)
        
        result = MiddlewareUtils.get_request()
        assert result == test_scope

    def test_set_request(self):
        """Test MiddlewareUtils.set_request method."""
        test_scope = {"type": "websocket"}
        MiddlewareUtils.set_request(test_scope)
        
        # Verify it was set
        assert MiddlewareUtils.get_request() == test_scope

    def test_set_request_none(self):
        """Test MiddlewareUtils.set_request with None."""
        MiddlewareUtils.set_request(None)
        assert MiddlewareUtils.get_request() is None


def test_get_middleware_positions():
    """Test get_middleware_positions function."""
    positions = get_middleware_positions()
    
    assert isinstance(positions, dict)
    assert "PROCESS_TIME" in positions
    assert "CSRF" in positions
    assert positions["PROCESS_TIME"] == 0


def test_middleware_constants():
    """Test middleware constants and attributes."""
    assert MiddlewareUtils.scope_name == "__starlette_caches__"
    assert hasattr(MiddlewareUtils, "_request_ctx_var")
    assert hasattr(MiddlewareUtils, "secure_headers")


def test_middleware_position_enum():
    """Test MiddlewarePosition enum values."""
    assert MiddlewarePosition.PROCESS_TIME == 0
    assert MiddlewarePosition.CSRF == 1
    assert MiddlewarePosition.SESSION == 2
    assert MiddlewarePosition.HTMX == 3
    assert MiddlewarePosition.CURRENT_REQUEST == 4
    assert MiddlewarePosition.COMPRESSION == 5
    assert MiddlewarePosition.SECURITY_HEADERS == 6