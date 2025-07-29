# Changelog

All notable changes to the Evion library will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release planning

## [0.1.0] - 2024-01-XX

### Added
- Initial release of the Evion library
- `EvionClient` class for API interactions
- `PredictionResult` class for handling results
- Support for single image NDVI prediction
- Support for batch image processing
- PIL Image integration
- Comprehensive error handling with custom exceptions
- File path, bytes, and BytesIO input support
- Automatic output path handling
- Health check functionality
- Complete test suite with pytest
- Comprehensive documentation and examples

### Features
- **Easy API integration** - Simple client initialization with API key
- **Multiple input formats** - Support for file paths, bytes, and PIL Images
- **Batch processing** - Process multiple images efficiently
- **Error handling** - Custom exceptions for different error types
- **PIL integration** - Seamless integration with Python Imaging Library
- **Flexible output** - Save to files or work with image data directly
- **Health checks** - Validate API connectivity and key status

### Supported Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)
- TIFF (.tiff, .tif)
- BMP (.bmp)

### Requirements
- Python >= 3.8
- requests >= 2.28.0
- Pillow >= 9.0.0

[Unreleased]: https://github.com/your-username/evion/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/your-username/evion/releases/tag/v0.1.0 