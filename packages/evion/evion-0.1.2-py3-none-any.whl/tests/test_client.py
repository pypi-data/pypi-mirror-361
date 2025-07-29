"""
Unit tests for the EvionClient class.
"""

import pytest
import io
import os
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import requests

import evion
from evion.client import EvionClient, PredictionResult
from evion.exceptions import (
    ValidationError,
    AuthenticationError,
    APIError,
    NetworkError,
    FileError
)


class TestEvionClient:
    """Test cases for the EvionClient class."""
    
    def test_init_with_api_key(self):
        """Test client initialization with API key."""
        client = EvionClient(api_key="test-key")
        assert client.api_key == "test-key"
        assert client.base_url == "https://evion.ai"
        assert client.timeout == 30
        assert client.session.headers["X-API-Key"] == "test-key"
    
    def test_init_with_custom_params(self):
        """Test client initialization with custom parameters."""
        client = EvionClient(
            api_key="test-key",
            base_url="https://custom.com",
            timeout=60
        )
        assert client.base_url == "https://custom.com"
        assert client.timeout == 60
    
    def test_init_without_api_key(self):
        """Test client initialization without API key raises error."""
        with pytest.raises(ValidationError, match="API key is required"):
            EvionClient(api_key="")
    
    def test_validate_image_file_valid(self, tmp_path):
        """Test image file validation with valid image."""
        # Create a test image
        test_image = Image.new('RGB', (100, 100), 'red')
        image_path = tmp_path / "test.jpg"
        test_image.save(image_path)
        
        client = EvionClient(api_key="test-key")
        result = client._validate_image_file(image_path)
        assert result == image_path
    
    def test_validate_image_file_not_found(self):
        """Test image file validation with non-existent file."""
        client = EvionClient(api_key="test-key")
        with pytest.raises(FileError, match="Image file not found"):
            client._validate_image_file("non-existent.jpg")
    
    def test_validate_image_file_invalid_extension(self, tmp_path):
        """Test image file validation with invalid extension."""
        # Create a text file with image extension
        text_file = tmp_path / "test.txt"
        text_file.write_text("not an image")
        
        client = EvionClient(api_key="test-key")
        with pytest.raises(ValidationError, match="Unsupported file format"):
            client._validate_image_file(text_file)
    
    def test_validate_image_bytes_valid(self):
        """Test image bytes validation with valid image."""
        # Create test image bytes
        test_image = Image.new('RGB', (100, 100), 'blue')
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format='JPEG')
        img_bytes_data = img_bytes.getvalue()
        
        client = EvionClient(api_key="test-key")
        result = client._validate_image_bytes(img_bytes_data)
        assert result == img_bytes_data
    
    def test_validate_image_bytes_empty(self):
        """Test image bytes validation with empty bytes."""
        client = EvionClient(api_key="test-key")
        with pytest.raises(ValidationError, match="Image bytes cannot be empty"):
            client._validate_image_bytes(b"")
    
    def test_validate_image_bytes_invalid(self):
        """Test image bytes validation with invalid bytes."""
        client = EvionClient(api_key="test-key")
        with pytest.raises(ValidationError, match="Invalid image bytes"):
            client._validate_image_bytes(b"not an image")
    
    @patch('evion.client.requests.Session.request')
    def test_make_request_success(self, mock_request):
        """Test successful API request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        client = EvionClient(api_key="test-key")
        result = client._make_request('GET', '/test')
        
        assert result == mock_response
        mock_request.assert_called_once()
    
    @patch('evion.client.requests.Session.request')
    def test_make_request_authentication_error(self, mock_request):
        """Test API request with authentication error."""
        # Mock 401 response
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 401
        mock_request.return_value = mock_response
        
        client = EvionClient(api_key="test-key")
        with pytest.raises(AuthenticationError, match="Invalid API key"):
            client._make_request('GET', '/test')
    
    @patch('evion.client.requests.Session.request')
    def test_make_request_network_error(self, mock_request):
        """Test API request with network error."""
        # Mock connection error
        mock_request.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        client = EvionClient(api_key="test-key")
        with pytest.raises(NetworkError, match="Failed to connect to the API"):
            client._make_request('GET', '/test')
    
    @patch('evion.client.requests.Session.request')
    def test_make_request_timeout(self, mock_request):
        """Test API request with timeout."""
        # Mock timeout error
        mock_request.side_effect = requests.exceptions.Timeout("Request timed out")
        
        client = EvionClient(api_key="test-key")
        with pytest.raises(NetworkError, match="Request timed out"):
            client._make_request('GET', '/test')
    
    @patch.object(EvionClient, '_make_request')
    def test_predict_success(self, mock_request, tmp_path):
        """Test successful prediction."""
        # Create test image
        test_image = Image.new('RGB', (100, 100), 'green')
        image_path = tmp_path / "test.jpg"
        test_image.save(image_path)
        
        # Mock successful response
        mock_response = Mock()
        mock_response.content = b"fake image data"
        mock_request.return_value = mock_response
        
        client = EvionClient(api_key="test-key")
        result = client.predict(str(image_path))
        
        assert isinstance(result, PredictionResult)
        assert result.success
        assert result.image_data == b"fake image data"
        mock_request.assert_called_once()
    
    @patch.object(EvionClient, '_make_request')
    def test_predict_with_bytes(self, mock_request):
        """Test prediction with image bytes."""
        # Create test image bytes
        test_image = Image.new('RGB', (100, 100), 'red')
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format='JPEG')
        img_bytes_data = img_bytes.getvalue()
        
        # Mock successful response
        mock_response = Mock()
        mock_response.content = b"fake ndvi data"
        mock_request.return_value = mock_response
        
        client = EvionClient(api_key="test-key")
        result = client.predict(img_bytes_data)
        
        assert result.success
        assert result.image_data == b"fake ndvi data"
    
    @patch.object(EvionClient, '_make_request')
    def test_predict_with_output_path(self, mock_request, tmp_path):
        """Test prediction with output path."""
        # Create test image
        test_image = Image.new('RGB', (100, 100), 'blue')
        image_path = tmp_path / "test.jpg"
        test_image.save(image_path)
        
        output_path = tmp_path / "output.png"
        
        # Mock successful response
        mock_response = Mock()
        mock_response.content = b"fake image data"
        mock_request.return_value = mock_response
        
        client = EvionClient(api_key="test-key")
        result = client.predict(str(image_path), output_path=str(output_path))
        
        assert result.success
        assert output_path.exists()
    
    def test_predict_invalid_image_type(self):
        """Test prediction with invalid image type."""
        client = EvionClient(api_key="test-key")
        with pytest.raises(ValidationError, match="Image must be a file path"):
            client.predict(123)  # Invalid type
    
    @patch.object(EvionClient, '_make_request')
    def test_health_check_success(self, mock_request):
        """Test successful health check."""
        # Mock successful response
        mock_response = Mock()
        mock_response.ok = True
        mock_request.return_value = mock_response
        
        client = EvionClient(api_key="test-key")
        result = client.health_check()
        
        assert result['status'] == 'healthy'
        assert result['api_key_valid'] is True
    
    @patch.object(EvionClient, '_make_request')
    def test_health_check_auth_error(self, mock_request):
        """Test health check with authentication error."""
        # Mock authentication error
        mock_request.side_effect = AuthenticationError("Invalid API key")
        
        client = EvionClient(api_key="test-key")
        result = client.health_check()
        
        assert result['status'] == 'error'
        assert result['api_key_valid'] is False


class TestPredictionResult:
    """Test cases for the PredictionResult class."""
    
    def test_success_with_data(self):
        """Test successful result with data."""
        client = EvionClient(api_key="test-key")
        result = PredictionResult(
            image_data=b"test data",
            original_image=b"original data",
            client=client
        )
        
        assert result.success is True
        assert result.image_data == b"test data"
        assert result.original_image == b"original data"
        assert result.error is None
    
    def test_failure_with_error(self):
        """Test failed result with error."""
        client = EvionClient(api_key="test-key")
        error = ValidationError("Test error")
        result = PredictionResult(
            image_data=None,
            original_image=None,
            client=client,
            error=error
        )
        
        assert result.success is False
        assert result.error == error
    
    def test_save_success(self, tmp_path):
        """Test saving result to file."""
        client = EvionClient(api_key="test-key")
        test_data = b"test image data"
        result = PredictionResult(
            image_data=test_data,
            original_image=b"original",
            client=client
        )
        
        output_path = tmp_path / "output.png"
        saved_path = result.save(str(output_path))
        
        assert saved_path == output_path
        assert output_path.exists()
        assert output_path.read_bytes() == test_data
    
    def test_save_failure(self):
        """Test saving failed result."""
        client = EvionClient(api_key="test-key")
        error = ValidationError("Test error")
        result = PredictionResult(
            image_data=None,
            original_image=None,
            client=client,
            error=error
        )
        
        with pytest.raises(ValidationError, match="Test error"):
            result.save("output.png")
    
    def test_to_pil_success(self):
        """Test converting result to PIL Image."""
        # Create test image data
        test_image = Image.new('RGB', (50, 50), 'yellow')
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format='PNG')
        img_data = img_bytes.getvalue()
        
        client = EvionClient(api_key="test-key")
        result = PredictionResult(
            image_data=img_data,
            original_image=b"original",
            client=client
        )
        
        pil_image = result.to_pil()
        assert isinstance(pil_image, Image.Image)
        assert pil_image.size == (50, 50)
    
    def test_to_pil_failure(self):
        """Test converting failed result to PIL Image."""
        client = EvionClient(api_key="test-key")
        error = ValidationError("Test error")
        result = PredictionResult(
            image_data=None,
            original_image=None,
            client=client,
            error=error
        )
        
        with pytest.raises(ValidationError, match="Test error"):
            result.to_pil()
    
    def test_to_bytes_success(self):
        """Test getting raw bytes from result."""
        client = EvionClient(api_key="test-key")
        test_data = b"test image bytes"
        result = PredictionResult(
            image_data=test_data,
            original_image=b"original",
            client=client
        )
        
        bytes_data = result.to_bytes()
        assert bytes_data == test_data
    
    def test_to_bytes_failure(self):
        """Test getting bytes from failed result."""
        client = EvionClient(api_key="test-key")
        error = ValidationError("Test error")
        result = PredictionResult(
            image_data=None,
            original_image=None,
            client=client,
            error=error
        )
        
        with pytest.raises(ValidationError, match="Test error"):
            result.to_bytes()
    
    def test_repr_success(self):
        """Test string representation of successful result."""
        client = EvionClient(api_key="test-key")
        result = PredictionResult(
            image_data=b"test data",
            original_image=b"original",
            client=client
        )
        
        repr_str = repr(result)
        assert "PredictionResult" in repr_str
        assert "9 bytes" in repr_str
    
    def test_repr_failure(self):
        """Test string representation of failed result."""
        client = EvionClient(api_key="test-key")
        error = ValidationError("Test error")
        result = PredictionResult(
            image_data=None,
            original_image=None,
            client=client,
            error=error
        )
        
        repr_str = repr(result)
        assert "PredictionResult" in repr_str
        assert "Error" in repr_str
        assert "Test error" in repr_str


# Fixtures for testing
@pytest.fixture
def sample_image_bytes():
    """Create sample image bytes for testing."""
    test_image = Image.new('RGB', (100, 100), 'red')
    img_bytes = io.BytesIO()
    test_image.save(img_bytes, format='JPEG')
    return img_bytes.getvalue()


@pytest.fixture
def mock_client():
    """Create a mock client for testing."""
    return EvionClient(api_key="test-key") 