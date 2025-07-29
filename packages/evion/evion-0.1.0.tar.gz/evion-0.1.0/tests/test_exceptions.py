"""
Unit tests for the exceptions module.
"""

import pytest
from evion.exceptions import (
    EvionError,
    AuthenticationError,
    APIError,
    ValidationError,
    NetworkError,
    FileError
)


class TestEvionExceptions:
    """Test cases for Evion exceptions."""
    
    def test_evion_error_base(self):
        """Test base EvionError exception."""
        error = EvionError("Base error message")
        assert str(error) == "Base error message"
        assert isinstance(error, Exception)
    
    def test_authentication_error(self):
        """Test AuthenticationError exception."""
        error = AuthenticationError("Invalid API key")
        assert str(error) == "Invalid API key"
        assert isinstance(error, EvionError)
    
    def test_api_error_basic(self):
        """Test APIError exception with basic message."""
        error = APIError("API request failed")
        assert str(error) == "API request failed"
        assert error.status_code is None
        assert error.response is None
        assert isinstance(error, EvionError)
    
    def test_api_error_with_details(self):
        """Test APIError exception with status code and response."""
        mock_response = {"error": "Bad request"}
        error = APIError("API request failed", status_code=400, response=mock_response)
        
        assert str(error) == "API request failed"
        assert error.status_code == 400
        assert error.response == mock_response
    
    def test_validation_error(self):
        """Test ValidationError exception."""
        error = ValidationError("Invalid input format")
        assert str(error) == "Invalid input format"
        assert isinstance(error, EvionError)
    
    def test_network_error(self):
        """Test NetworkError exception."""
        error = NetworkError("Connection timeout")
        assert str(error) == "Connection timeout"
        assert isinstance(error, EvionError)
    
    def test_file_error(self):
        """Test FileError exception."""
        error = FileError("File not found")
        assert str(error) == "File not found"
        assert isinstance(error, EvionError)
    
    def test_exception_inheritance(self):
        """Test that all exceptions inherit from EvionError."""
        exceptions = [
            AuthenticationError("test"),
            APIError("test"),
            ValidationError("test"),
            NetworkError("test"),
            FileError("test")
        ]
        
        for exc in exceptions:
            assert isinstance(exc, EvionError)
            assert isinstance(exc, Exception)
    
    def test_exception_with_empty_message(self):
        """Test exceptions with empty messages."""
        error = EvionError("")
        assert str(error) == ""
    
    def test_exception_with_none_message(self):
        """Test exceptions with None message."""
        error = EvionError(None)
        assert str(error) == "None" 