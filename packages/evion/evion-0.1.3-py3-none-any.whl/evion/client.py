"""
Main client class for interacting with the Evion NDVI API.
"""

import os
import io
import requests
from typing import Union, Optional, Dict, Any
from pathlib import Path
from PIL import Image

from .exceptions import (
    EvionError,
    AuthenticationError,
    APIError,
    ValidationError,
    NetworkError,
    FileError
)


class EvionClient:
    """
    Client for interacting with the Evion NDVI prediction API.
    
    This client allows you to upload images and get NDVI (Normalized Difference 
    Vegetation Index) predictions using your API key.
    
    Args:
        api_key (str): Your Evion API key
        base_url (str, optional): Base URL for the API. Defaults to production URL.
        timeout (int, optional): Request timeout in seconds. Defaults to 30.
    
    Example:
        >>> client = EvionClient(api_key="your-api-key")
        >>> result = client.predict("path/to/image.jpg")
        >>> result.save("ndvi_result.png")
    """
    
    def __init__(
        self, 
        api_key: str, 
        base_url: Optional[str] = None,
        timeout: int = 30
    ):
        if not api_key:
            raise ValidationError("API key is required")
        self.api_key = api_key
        # Auto-detect base_url: env var > provided > prod > localhost
        env_url = os.environ.get("EVION_API_URL")
        self.base_url = base_url or env_url or "https://evion.ai"
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": self.api_key,
            "User-Agent": f"evion-python/{self._get_version()}"
        })
    
    def _get_version(self) -> str:
        """Get the library version."""
        try:
            from . import __version__
            return __version__
        except ImportError:
            return "unknown"
    
    def _validate_image_file(self, image_path: Union[str, Path]) -> Path:
        """Validate that the image file exists and is a valid image."""
        path = Path(image_path)
        
        if not path.exists():
            raise FileError(f"Image file not found: {path}")
        
        if not path.is_file():
            raise FileError(f"Path is not a file: {path}")
        
        # Check file extension
        valid_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp'}
        if path.suffix.lower() not in valid_extensions:
            raise ValidationError(
                f"Unsupported file format: {path.suffix}. "
                f"Supported formats: {', '.join(valid_extensions)}"
            )
        
        # Try to open the image to validate it
        try:
            with Image.open(path) as img:
                img.verify()
        except Exception as e:
            raise ValidationError(f"Invalid image file: {e}")
        
        return path
    
    def _validate_image_bytes(self, image_bytes: bytes) -> bytes:
        """Validate image bytes."""
        if not image_bytes:
            raise ValidationError("Image bytes cannot be empty")
        
        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                img.verify()
        except Exception as e:
            raise ValidationError(f"Invalid image bytes: {e}")
        
        return image_bytes
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make an HTTP request with error handling and auto-fallback for base_url."""
        tried_urls = []
        urls_to_try = [self.base_url]
        # If not explicitly set, try localhost as fallback
        if not (self.base_url and self.base_url.startswith("http://localhost")):
            urls_to_try.append("http://localhost:5000")
        last_exc = None
        for url_base in urls_to_try:
            url = f"{url_base.rstrip('/')}/{endpoint.lstrip('/')}"
            tried_urls.append(url)
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    **kwargs
                )
            except requests.exceptions.Timeout:
                last_exc = NetworkError(f"Request timed out for {url}")
                continue
            except requests.exceptions.ConnectionError:
                last_exc = NetworkError(f"Failed to connect to the API at {url}")
                continue
            except requests.exceptions.RequestException as e:
                last_exc = NetworkError(f"Network error at {url}: {e}")
                continue
            # Handle HTTP errors
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 403:
                raise AuthenticationError("API key is inactive or insufficient permissions")
            elif response.status_code == 429:
                raise APIError("Rate limit exceeded", status_code=429, response=response)
            elif response.status_code == 405:
                last_exc = APIError(
                    f"HTTP 405 at {url}. This usually means the endpoint does not exist or the method is wrong. "
                    f"Check your base_url and backend server.",
                    status_code=405, response=response)
                continue
            elif not response.ok:
                try:
                    error_data = response.json()
                    error_message = error_data.get('error', f'HTTP {response.status_code}')
                except:
                    error_message = f'HTTP {response.status_code}'
                last_exc = APIError(
                    f"{error_message} at {url}",
                    status_code=response.status_code,
                    response=response
                )
                continue
            return response
        # If all attempts failed
        msg = (
            f"Failed to connect to any Evion API endpoint.\n"
            f"Tried URLs: {tried_urls}\n"
            f"Set the EVION_API_URL environment variable or pass base_url to EvionClient.\n"
            f"Last error: {last_exc}"
        )
        raise NetworkError(msg)
    
    def predict(
        self, 
        image: Union[str, Path, bytes, io.BytesIO],
        output_path: Optional[Union[str, Path]] = None
    ) -> 'PredictionResult':
        """
        Generate NDVI prediction for an image.
        
        Args:
            image: Path to image file, image bytes, or BytesIO object
            output_path: Optional path to save the result image
            
        Returns:
            PredictionResult: Object containing the prediction results
            
        Raises:
            ValidationError: If image is invalid
            AuthenticationError: If API key is invalid
            APIError: If API request fails
            NetworkError: If network request fails
            
        Example:
            >>> result = client.predict("satellite_image.jpg")
            >>> result.save("ndvi_output.png")
        """
        # Prepare the image data
        if isinstance(image, (str, Path)):
            image_path = self._validate_image_file(image)
            with open(image_path, 'rb') as f:
                image_data = f.read()
            filename = image_path.name
        elif isinstance(image, bytes):
            image_data = self._validate_image_bytes(image)
            filename = "image.jpg"
        elif isinstance(image, io.BytesIO):
            image_data = image.getvalue()
            image_data = self._validate_image_bytes(image_data)
            filename = "image.jpg"
        else:
            raise ValidationError(
                "Image must be a file path, bytes, or BytesIO object"
            )
        
        # Prepare the request
        files = {
            'image': (filename, image_data, 'image/jpeg')
        }
        
        # Make the API request
        response = self._make_request('POST', '/process-ndvi', files=files)
        
        # Create result object
        result = PredictionResult(
            image_data=response.content,
            original_image=image_data,
            client=self
        )
        
        # Save to output path if provided
        if output_path:
            result.save(output_path)
        
        return result
    
    def predict_batch(
        self, 
        images: list,
        output_dir: Optional[Union[str, Path]] = None
    ) -> list:
        """
        Generate NDVI predictions for multiple images.
        
        Args:
            images: List of image paths, bytes, or BytesIO objects
            output_dir: Optional directory to save result images
            
        Returns:
            List of PredictionResult objects
            
        Example:
            >>> results = client.predict_batch(["img1.jpg", "img2.jpg"])
            >>> for i, result in enumerate(results):
            ...     result.save(f"result_{i}.png")
        """
        results = []
        
        for i, image in enumerate(images):
            try:
                output_path = None
                if output_dir:
                    output_dir = Path(output_dir)
                    output_dir.mkdir(parents=True, exist_ok=True)
                    output_path = output_dir / f"ndvi_result_{i}.png"
                
                result = self.predict(image, output_path)
                results.append(result)
                
            except Exception as e:
                # Add error information to the result
                error_result = PredictionResult(
                    image_data=None,
                    original_image=None,
                    client=self,
                    error=e
                )
                results.append(error_result)
        
        return results
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check API health and key validity.
        
        Returns:
            Dict containing health status information
            
        Example:
            >>> status = client.health_check()
            >>> print(status['status'])  # 'healthy'
        """
        try:
            # Try a simple request to validate the API key
            response = self._make_request('GET', '/api/health')
            return {
                'status': 'healthy',
                'api_key_valid': True,
                'message': 'API is accessible and key is valid'
            }
        except AuthenticationError:
            return {
                'status': 'error',
                'api_key_valid': False,
                'message': 'Invalid API key'
            }
        except Exception as e:
            return {
                'status': 'error',
                'api_key_valid': None,
                'message': str(e)
            }


class PredictionResult:
    """
    Container for NDVI prediction results.
    
    Attributes:
        image_data (bytes): The processed NDVI image data
        original_image (bytes): The original input image data
        error (Exception): Any error that occurred during processing
    """
    
    def __init__(
        self, 
        image_data: Optional[bytes],
        original_image: Optional[bytes],
        client: EvionClient,
        error: Optional[Exception] = None
    ):
        self.image_data = image_data
        self.original_image = original_image
        self.client = client
        self.error = error
    
    @property
    def success(self) -> bool:
        """Check if the prediction was successful."""
        return self.error is None and self.image_data is not None
    
    def save(self, output_path: Union[str, Path]) -> Path:
        """
        Save the NDVI result image to a file.
        
        Args:
            output_path: Path where to save the image
            
        Returns:
            Path object of the saved file
            
        Raises:
            FileError: If saving fails
            ValidationError: If no image data to save
        """
        if not self.success:
            if self.error:
                raise self.error
            else:
                raise ValidationError("No image data to save")
        
        output_path = Path(output_path)
        
        try:
            # Create parent directories if they don't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the image data
            with open(output_path, 'wb') as f:
                f.write(self.image_data)
            
            return output_path
            
        except Exception as e:
            raise FileError(f"Failed to save image: {e}")
    
    def to_pil(self) -> Image.Image:
        """
        Convert the result to a PIL Image object.
        
        Returns:
            PIL Image object
            
        Raises:
            ValidationError: If no image data available
        """
        if not self.success:
            if self.error:
                raise self.error
            else:
                raise ValidationError("No image data available")
        
        return Image.open(io.BytesIO(self.image_data))
    
    def to_bytes(self) -> bytes:
        """
        Get the raw image bytes.
        
        Returns:
            Raw image bytes
            
        Raises:
            ValidationError: If no image data available
        """
        if not self.success:
            if self.error:
                raise self.error
            else:
                raise ValidationError("No image data available")
        
        return self.image_data
    
    def __repr__(self) -> str:
        if self.success:
            return f"<PredictionResult: {len(self.image_data)} bytes>"
        else:
            return f"<PredictionResult: Error - {self.error}>" 