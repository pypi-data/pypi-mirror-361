#!/usr/bin/env python3
"""
Batch processing example for the Evion library.

This script demonstrates how to:
1. Process multiple images at once
2. Handle individual failures gracefully
3. Show progress with a progress bar
4. Save results with organized naming
"""

import evion
import os
import glob
from pathlib import Path

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
    
    # Find all image files in the input directory
    input_dir = "input_images"
    if not os.path.exists(input_dir):
        print(f"Input directory not found: {input_dir}")
        print("Please create the directory and add some images.")
        return
    
    # Supported image extensions
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.tiff', '*.tif', '*.bmp']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(input_dir, ext)))
        image_files.extend(glob.glob(os.path.join(input_dir, ext.upper())))
    
    if not image_files:
        print(f"No image files found in {input_dir}")
        return
    
    print(f"Found {len(image_files)} images to process")
    
    # Create output directory
    output_dir = "ndvi_results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Process images with progress tracking
    successful = 0
    failed = 0
    
    try:
        # Try to import tqdm for progress bar
        from tqdm import tqdm
        progress_bar = tqdm(image_files, desc="Processing images")
    except ImportError:
        # Fallback to simple enumeration
        progress_bar = enumerate(image_files, 1)
        print("Install tqdm for progress bar: pip install tqdm")
    
    for i, image_path in enumerate(progress_bar, 1):
        try:
            # Get the base filename without extension
            base_name = Path(image_path).stem
            output_path = os.path.join(output_dir, f"ndvi_{base_name}.png")
            
            # Update progress description if using tqdm
            if hasattr(progress_bar, 'set_description'):
                progress_bar.set_description(f"Processing {base_name}")
            else:
                print(f"Processing {i}/{len(image_files)}: {base_name}")
            
            # Analyze the image
            result = client.predict(image_path, output_path=output_path)
            
            if result.success:
                successful += 1
                print(f"✅ {base_name} - Success")
            else:
                failed += 1
                print(f"❌ {base_name} - Failed: {result.error}")
                
        except Exception as e:
            failed += 1
            print(f"❌ {Path(image_path).name} - Error: {e}")
    
    # Summary
    print(f"\n📊 Processing Summary:")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📁 Results saved to: {output_dir}")
    
    if successful > 0:
        print(f"\n🎉 Successfully processed {successful} images!")
    
    if failed > 0:
        print(f"\n⚠️  {failed} images failed to process.")

def batch_processing_simple():
    """
    Alternative approach using the built-in batch processing method.
    """
    api_key = os.getenv('EVION_API_KEY')
    if not api_key:
        print("Please set the EVION_API_KEY environment variable")
        return
    
    client = evion.EvionClient(api_key=api_key)
    
    # List of images to process
    image_files = ["img1.jpg", "img2.jpg", "img3.jpg"]
    
    # Process all images at once
    print("Processing batch of images...")
    results = client.predict_batch(image_files, output_dir="batch_results")
    
    # Check results
    for i, result in enumerate(results):
        image_name = image_files[i]
        if result.success:
            print(f"✅ {image_name} - Success")
        else:
            print(f"❌ {image_name} - Failed: {result.error}")

if __name__ == "__main__":
    # Run the main batch processing example
    main()
    
    # Uncomment to run the simple batch processing example
    # batch_processing_simple() 