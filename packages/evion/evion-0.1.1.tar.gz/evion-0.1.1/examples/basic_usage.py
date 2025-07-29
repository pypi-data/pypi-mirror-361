#!/usr/bin/env python3
"""
Basic usage example for the Evion library.

This script demonstrates how to:
1. Initialize the Evion client
2. Analyze a single image
3. Save the result
4. Handle errors
"""

import evion
import os

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
    print("Checking API health...")
    health = client.health_check()
    print(f"API Status: {health['status']}")
    print(f"API Key Valid: {health['api_key_valid']}")
    
    if not health['api_key_valid']:
        print("Invalid API key! Please check your credentials.")
        return
    
    # Example image path (replace with your image)
    image_path = "sample_image.jpg"
    
    if not os.path.exists(image_path):
        print(f"Image file not found: {image_path}")
        print("Please provide a valid image file path.")
        return
    
    try:
        print(f"Analyzing image: {image_path}")
        
        # Analyze the image
        result = client.predict(image_path)
        
        if result.success:
            print("✅ Analysis successful!")
            
            # Save the result
            output_path = "ndvi_result.png"
            result.save(output_path)
            print(f"📁 Result saved to: {output_path}")
            
            # Print some info about the result
            print(f"📊 Result image size: {len(result.image_data)} bytes")
            
        else:
            print(f"❌ Analysis failed: {result.error}")
            
    except evion.AuthenticationError:
        print("❌ Authentication failed - check your API key")
    except evion.ValidationError as e:
        print(f"❌ Validation error: {e}")
    except evion.APIError as e:
        print(f"❌ API error: {e}")
    except evion.NetworkError:
        print("❌ Network error - check your internet connection")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main() 