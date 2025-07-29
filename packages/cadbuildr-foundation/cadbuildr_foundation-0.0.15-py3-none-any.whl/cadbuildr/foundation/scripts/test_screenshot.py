#!/usr/bin/env python3

import base64
from cadbuildr.foundation.utils_websocket import get_screenshot

def test_screenshot():
    """Simple test to request a screenshot."""
    
    try:
        
        print("Requesting screenshot...")
        print("Make sure your viewer is open and displaying something!")
        
        # Request screenshot with timeout
        img_data = get_screenshot(timeout=10)
        
        if img_data:
            print(f"✅ Screenshot received! Length: {len(img_data)} characters")
            
            # Check if it's a proper data URL
            if img_data.startswith('data:image/png;base64,'):
                print("✅ Screenshot has proper data URL format")
                base64_data = img_data.split(',', 1)[1]
            else:
                print("ℹ️  Screenshot is raw base64 data")
                base64_data = img_data
            
            # Decode and save
            try:
                image_bytes = base64.b64decode(base64_data)
                output_file = "screenshot_test.png"
                
                with open(output_file, 'wb') as f:
                    f.write(image_bytes)
                
                print(f"✅ Screenshot saved to {output_file}")
                print(f"📁 File size: {len(image_bytes)} bytes")
                
            except Exception as decode_error:
                print(f"❌ Failed to decode/save image: {decode_error}")
                print(f"First 100 chars of data: {img_data[:100]}...")
            
        else:
            print("❌ Screenshot data is None/empty")
            
    except Exception as e:
        print(f"❌ Screenshot failed: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_screenshot() 