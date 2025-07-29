#!/usr/bin/env python3
"""
PIL integration example for the Evion library.

This script demonstrates how to:
1. Work with PIL Images
2. Convert between different formats
3. Display images
4. Apply additional processing
"""

import evion
import os
import io
from PIL import Image, ImageEnhance, ImageDraw, ImageFont

def main():
    # Get API key from environment variable
    api_key = os.getenv('EVION_API_KEY')
    if not api_key:
        print("Please set the EVION_API_KEY environment variable")
        print("Example: export EVION_API_KEY='your-api-key-here'")
        return
    
    # Initialize the client
    print("Initializing Evion client...")
    client = evion.EvionClient(api_key=api_key)
    
    # Check API health
    health = client.health_check()
    if not health['api_key_valid']:
        print("Invalid API key! Please check your credentials.")
        return
    
    # Example 1: Load image with PIL and analyze
    print("\n🖼️  Example 1: PIL Image Processing")
    
    image_path = "sample_image.jpg"
    if not os.path.exists(image_path):
        print(f"Image file not found: {image_path}")
        print("Please provide a valid image file.")
        return
    
    # Open image with PIL
    print(f"Loading image: {image_path}")
    original_image = Image.open(image_path)
    
    # Display original image info
    print(f"Original image size: {original_image.size}")
    print(f"Original image mode: {original_image.mode}")
    
    # Convert PIL image to bytes for analysis
    img_bytes = io.BytesIO()
    original_image.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    # Analyze with Evion
    print("Analyzing image...")
    result = client.predict(img_bytes)
    
    if result.success:
        print("✅ Analysis successful!")
        
        # Convert result back to PIL Image
        ndvi_image = result.to_pil()
        
        print(f"NDVI result size: {ndvi_image.size}")
        print(f"NDVI result mode: {ndvi_image.mode}")
        
        # Save the result
        ndvi_image.save("ndvi_result_pil.png")
        print("📁 NDVI result saved as: ndvi_result_pil.png")
        
        # Example 2: Create a comparison image
        print("\n🔍 Example 2: Creating Comparison Image")
        create_comparison_image(original_image, ndvi_image)
        
        # Example 3: Apply additional processing
        print("\n✨ Example 3: Additional Processing")
        apply_additional_processing(ndvi_image)
        
        # Example 4: Extract statistics
        print("\n📊 Example 4: Extract Statistics")
        extract_statistics(ndvi_image)
        
    else:
        print(f"❌ Analysis failed: {result.error}")

def create_comparison_image(original, ndvi):
    """Create a side-by-side comparison image."""
    
    # Ensure both images have the same height
    if original.size[1] != ndvi.size[1]:
        # Resize to match the smaller height
        target_height = min(original.size[1], ndvi.size[1])
        original = original.resize((
            int(original.size[0] * target_height / original.size[1]),
            target_height
        ))
        ndvi = ndvi.resize((
            int(ndvi.size[0] * target_height / ndvi.size[1]),
            target_height
        ))
    
    # Create a new image with combined width
    total_width = original.size[0] + ndvi.size[0] + 20  # 20px gap
    comparison = Image.new('RGB', (total_width, original.size[1]), 'white')
    
    # Paste the images
    comparison.paste(original, (0, 0))
    comparison.paste(ndvi, (original.size[0] + 20, 0))
    
    # Add labels
    try:
        # Try to use a nice font
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    draw = ImageDraw.Draw(comparison)
    draw.text((10, 10), "Original", fill='black', font=font)
    draw.text((original.size[0] + 30, 10), "NDVI Analysis", fill='black', font=font)
    
    # Save the comparison
    comparison.save("comparison.png")
    print("📁 Comparison image saved as: comparison.png")

def apply_additional_processing(ndvi_image):
    """Apply additional processing to the NDVI result."""
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(ndvi_image)
    enhanced = enhancer.enhance(1.5)  # Increase contrast by 50%
    enhanced.save("ndvi_enhanced_contrast.png")
    print("📁 Enhanced contrast image saved as: ndvi_enhanced_contrast.png")
    
    # Adjust brightness
    enhancer = ImageEnhance.Brightness(ndvi_image)
    brightened = enhancer.enhance(1.2)  # Increase brightness by 20%
    brightened.save("ndvi_brightened.png")
    print("📁 Brightened image saved as: ndvi_brightened.png")
    
    # Convert to grayscale
    grayscale = ndvi_image.convert('L')
    grayscale.save("ndvi_grayscale.png")
    print("📁 Grayscale image saved as: ndvi_grayscale.png")

def extract_statistics(ndvi_image):
    """Extract basic statistics from the NDVI image."""
    
    # Convert to grayscale for analysis
    if ndvi_image.mode != 'L':
        gray = ndvi_image.convert('L')
    else:
        gray = ndvi_image
    
    # Get pixel values
    pixels = list(gray.getdata())
    
    # Calculate statistics
    total_pixels = len(pixels)
    min_value = min(pixels)
    max_value = max(pixels)
    avg_value = sum(pixels) / total_pixels
    
    # Count vegetation levels (assuming NDVI-like values)
    low_vegetation = sum(1 for p in pixels if p < 85)  # Low vegetation
    medium_vegetation = sum(1 for p in pixels if 85 <= p < 170)  # Medium vegetation
    high_vegetation = sum(1 for p in pixels if p >= 170)  # High vegetation
    
    print(f"📊 Image Statistics:")
    print(f"   Total pixels: {total_pixels:,}")
    print(f"   Value range: {min_value} - {max_value}")
    print(f"   Average value: {avg_value:.2f}")
    print(f"   Low vegetation: {low_vegetation:,} pixels ({low_vegetation/total_pixels*100:.1f}%)")
    print(f"   Medium vegetation: {medium_vegetation:,} pixels ({medium_vegetation/total_pixels*100:.1f}%)")
    print(f"   High vegetation: {high_vegetation:,} pixels ({high_vegetation/total_pixels*100:.1f}%)")

def advanced_pil_example():
    """
    Advanced example showing more PIL integration techniques.
    """
    api_key = os.getenv('EVION_API_KEY')
    if not api_key:
        return
    
    client = evion.EvionClient(api_key=api_key)
    
    # Create a synthetic image for testing
    print("\n🎨 Creating synthetic test image...")
    
    # Create a test image with different regions
    test_image = Image.new('RGB', (400, 400), 'brown')
    draw = ImageDraw.Draw(test_image)
    
    # Add some "vegetation" areas
    draw.rectangle([50, 50, 150, 150], fill='green')
    draw.rectangle([200, 200, 350, 350], fill='darkgreen')
    draw.ellipse([100, 250, 200, 350], fill='lightgreen')
    
    test_image.save("synthetic_test.png")
    print("📁 Synthetic test image saved as: synthetic_test.png")
    
    # Convert to bytes and analyze
    img_bytes = io.BytesIO()
    test_image.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    result = client.predict(img_bytes)
    
    if result.success:
        ndvi_result = result.to_pil()
        ndvi_result.save("synthetic_ndvi.png")
        print("📁 Synthetic NDVI result saved as: synthetic_ndvi.png")
        
        # Create a color-coded result
        create_color_coded_result(ndvi_result)

def create_color_coded_result(ndvi_image):
    """Create a color-coded visualization of NDVI results."""
    
    # Convert to RGB if needed
    if ndvi_image.mode != 'RGB':
        rgb_image = ndvi_image.convert('RGB')
    else:
        rgb_image = ndvi_image.copy()
    
    # Apply color mapping (this is a simple example)
    pixels = list(rgb_image.getdata())
    new_pixels = []
    
    for pixel in pixels:
        # Get the brightness value
        brightness = sum(pixel) // 3
        
        # Map to vegetation colors
        if brightness < 85:
            new_pixels.append((139, 69, 19))  # Brown - no vegetation
        elif brightness < 170:
            new_pixels.append((255, 255, 0))  # Yellow - low vegetation
        else:
            new_pixels.append((0, 255, 0))  # Green - high vegetation
    
    # Create new image with color-coded pixels
    color_coded = Image.new('RGB', rgb_image.size)
    color_coded.putdata(new_pixels)
    color_coded.save("ndvi_color_coded.png")
    print("📁 Color-coded NDVI saved as: ndvi_color_coded.png")

if __name__ == "__main__":
    main()
    
    # Uncomment to run the advanced example
    # advanced_pil_example() 