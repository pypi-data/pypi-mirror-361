# Evion - NDVI Vegetation Analysis Library

[![PyPI version](https://badge.fury.io/py/evion.svg)](https://badge.fury.io/py/evion)
[![Python versions](https://img.shields.io/pypi/pyversions/evion.svg)](https://pypi.org/project/evion/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Evion** is a Python library for vegetation analysis using NDVI (Normalized Difference Vegetation Index) powered by AI. Upload satellite or aerial images and get professional-grade vegetation analysis results.

## 🌱 Features

- **Easy-to-use API** - Just a few lines of code to get started
- **AI-powered analysis** - Advanced machine learning models for accurate NDVI calculation
- **Multiple input formats** - Support for various image formats (JPG, PNG, TIFF, etc.)
- **Batch processing** - Process multiple images at once
- **Flexible output** - Save results as files or work with PIL Images
- **Professional results** - High-quality vegetation analysis suitable for research and agriculture

## 🚀 Quick Start

### Installation

```bash
pip install evion
```

### Basic Usage

```python
import evion

# Initialize the client with your API key
client = evion.EvionClient(api_key="your-api-key-here")

# Analyze an image
result = client.predict("satellite_image.jpg")

# Save the result
result.save("ndvi_result.png")

print(f"Analysis complete! Success: {result.success}")
```

### Get Your API Key

1. Visit [evion.ai](https://evion.ai) and create an account
2. Navigate to your API Keys page
3. Create a new API key
4. Copy the key and use it in your code

## 📖 Documentation

### EvionClient

The main class for interacting with the Evion API.

#### Constructor

```python
client = evion.EvionClient(
    api_key="your-api-key",
    base_url="https://your-domain.com",  # Optional, defaults to production
    timeout=30  # Optional, request timeout in seconds
)
```

#### Methods

##### `predict(image, output_path=None)`

Analyze a single image for vegetation.

**Parameters:**
- `image`: Path to image file, image bytes, or BytesIO object
- `output_path`: Optional path to save the result image

**Returns:** `PredictionResult` object

**Example:**
```python
# From file path
result = client.predict("image.jpg")

# From bytes
with open("image.jpg", "rb") as f:
    result = client.predict(f.read())

# Save result automatically
result = client.predict("image.jpg", output_path="result.png")
```

##### `predict_batch(images, output_dir=None)`

Analyze multiple images at once.

**Parameters:**
- `images`: List of image paths, bytes, or BytesIO objects
- `output_dir`: Optional directory to save result images

**Returns:** List of `PredictionResult` objects

**Example:**
```python
images = ["img1.jpg", "img2.jpg", "img3.jpg"]
results = client.predict_batch(images, output_dir="results/")

for i, result in enumerate(results):
    if result.success:
        print(f"Image {i+1}: Analysis successful")
    else:
        print(f"Image {i+1}: Error - {result.error}")
```

##### `health_check()`

Check API health and validate your API key.

**Returns:** Dictionary with health status

**Example:**
```python
status = client.health_check()
print(f"API Status: {status['status']}")
print(f"API Key Valid: {status['api_key_valid']}")
```

### PredictionResult

Container for analysis results.

#### Properties

- `success`: Boolean indicating if analysis was successful
- `image_data`: Raw bytes of the result image
- `original_image`: Raw bytes of the original image
- `error`: Any error that occurred during processing

#### Methods

##### `save(output_path)`

Save the result image to a file.

```python
result.save("ndvi_output.png")
```

##### `to_pil()`

Convert result to a PIL Image object.

```python
pil_image = result.to_pil()
pil_image.show()  # Display the image
```

##### `to_bytes()`

Get the raw image bytes.

```python
image_bytes = result.to_bytes()
```

## 🔧 Advanced Usage

### Error Handling

```python
import evion

try:
    client = evion.EvionClient(api_key="your-api-key")
    result = client.predict("image.jpg")
    
    if result.success:
        result.save("output.png")
    else:
        print(f"Analysis failed: {result.error}")
        
except evion.AuthenticationError:
    print("Invalid API key")
except evion.ValidationError as e:
    print(f"Invalid input: {e}")
except evion.APIError as e:
    print(f"API error: {e}")
except evion.NetworkError:
    print("Network connection failed")
```

### Working with PIL Images

```python
from PIL import Image
import evion

client = evion.EvionClient(api_key="your-api-key")

# Open image with PIL
original = Image.open("satellite_image.jpg")

# Convert to bytes for analysis
import io
img_bytes = io.BytesIO()
original.save(img_bytes, format='JPEG')
img_bytes.seek(0)

# Analyze
result = client.predict(img_bytes)

# Get result as PIL Image
ndvi_image = result.to_pil()

# Display both images
original.show(title="Original")
ndvi_image.show(title="NDVI Analysis")
```

### Batch Processing with Progress

```python
import evion
from tqdm import tqdm

client = evion.EvionClient(api_key="your-api-key")

# Process multiple images with progress bar
image_paths = ["img1.jpg", "img2.jpg", "img3.jpg", "img4.jpg"]
results = []

for image_path in tqdm(image_paths, desc="Processing images"):
    try:
        result = client.predict(image_path)
        results.append(result)
        
        if result.success:
            # Save with descriptive name
            output_name = f"ndvi_{image_path.split('/')[-1]}"
            result.save(output_name)
            
    except Exception as e:
        print(f"Error processing {image_path}: {e}")

print(f"Processed {len(results)} images")
```

## 🌍 Use Cases

### Agriculture
- **Crop health monitoring** - Identify stressed or diseased areas
- **Yield prediction** - Estimate crop productivity
- **Irrigation planning** - Optimize water usage based on vegetation health

### Environmental Research
- **Forest monitoring** - Track deforestation and forest health
- **Climate studies** - Analyze vegetation response to climate change
- **Biodiversity assessment** - Monitor ecosystem health

### Urban Planning
- **Green space analysis** - Assess urban vegetation coverage
- **Environmental impact** - Evaluate development effects on vegetation
- **Sustainability planning** - Plan green infrastructure

## 📊 Supported Image Formats

- **JPEG** (.jpg, .jpeg)
- **PNG** (.png)
- **TIFF** (.tiff, .tif)
- **BMP** (.bmp)

## 🔒 Security

- All API communications are encrypted with HTTPS
- API keys are securely validated on each request
- No image data is stored permanently on our servers
- Full compliance with data protection regulations

## 🆘 Support

- **Documentation**: [docs.evion.ai](https://docs.evion.ai)
- **Issues**: [GitHub Issues](https://github.com/your-username/evion/issues)
- **Email**: support@evion.ai
- **Community**: [Discord](https://discord.gg/evion)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 🔄 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.

## 🏆 Credits

Evion is developed by the Evion Team with contributions from the open-source community.

---

**Ready to analyze vegetation like a pro?** Get started with Evion today! 🌱 