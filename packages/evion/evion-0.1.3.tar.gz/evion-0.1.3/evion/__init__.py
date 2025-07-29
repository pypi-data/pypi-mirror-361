"""
Evion - NDVI Prediction Library

A Python library for vegetation analysis using NDVI (Normalized Difference Vegetation Index).
Easily upload images and get AI-powered vegetation predictions.
"""

__version__ = "0.1.0"
__author__ = "Evion Team"
__email__ = "support@evion.ai"

from .client import EvionClient
from .exceptions import EvionError, AuthenticationError, APIError, ValidationError

__all__ = [
    "EvionClient",
    "EvionError", 
    "AuthenticationError",
    "APIError",
    "ValidationError"
] 