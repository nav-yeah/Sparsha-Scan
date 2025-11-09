"""
Test script to verify model loading and prediction
Run this to check if the model is working correctly
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from model_predictor import get_predictor
import numpy as np
from PIL import Image
import io

def test_model():
    """Test model loading and prediction"""
    print("=" * 70)
    print("TESTING SKIN DISEASE DETECTION MODEL")
    print("=" * 70)
    
    # Get predictor
    print("\n1. Initializing predictor...")
    predictor = get_predictor()
    
    print(f"\n   Model loaded: {predictor.is_loaded}")
    print(f"   Number of classes: {len(predictor.class_names)}")
    print(f"   Class names: {predictor.class_names[:5]}..." if len(predictor.class_names) > 5 else f"   Class names: {predictor.class_names}")
    
    if not predictor.is_loaded:
        print("\n❌ Model is not loaded. Cannot test predictions.")
        print("   Please check:")
        print("   - Model file exists at: mobilenet_dermnet_model_final.keras")
        print("   - TensorFlow is installed")
        print("   - Model file is not corrupted")
        return False
    
    # Test with dummy image
    print("\n2. Testing prediction with dummy image...")
    try:
        # Create a dummy RGB image
        dummy_img = Image.new('RGB', (128, 128), color='red')
        img_bytes = io.BytesIO()
        dummy_img.save(img_bytes, format='JPEG')
        img_bytes = img_bytes.getvalue()
        
        result = predictor.predict(img_bytes)
        
        if result.get("success"):
            print(f"   ✅ Prediction successful!")
            print(f"   Disease: {result['disease']}")
            print(f"   Confidence: {result['confidence']}%")
            print(f"   Method: {result['method']}")
            print(f"   Top predictions: {result.get('top_predictions', [])}")
            return True
        else:
            print(f"   ❌ Prediction failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error during prediction: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_model()
    print("\n" + "=" * 70)
    if success:
        print("✅ MODEL TEST PASSED")
    else:
        print("❌ MODEL TEST FAILED")
    print("=" * 70)
    sys.exit(0 if success else 1)

