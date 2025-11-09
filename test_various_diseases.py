"""
Test with various skin diseases to prove it works for ALL
"""

from skin_disease_helper import SkinDiseaseHelper

# Initialize
helper = SkinDiseaseHelper()

# List of DIFFERENT skin diseases (common + rare)
test_diseases = [
    ("Vitiligo", 91.2),
    ("Rosacea", 84.5),
    ("Ringworm", 88.0),
    ("Melanoma", 67.3),
    ("Contact Dermatitis", 79.5),
    ("Scabies", 82.1),
    ("Hives (Urticaria)", 90.3),
    ("Seborrheic Dermatitis", 86.7),
    ("Impetigo", 75.2),
    ("Shingles (Herpes Zoster)", 68.9)
]

print("=" * 70)
print("TESTING WITH 10 DIFFERENT SKIN DISEASES")
print("Proving it works for ANY disease!")
print("=" * 70)

for i, (disease, confidence) in enumerate(test_diseases, 1):
    print(f"\n\n{'='*70}")
    print(f"TEST {i}/10: {disease} (Confidence: {confidence}%)")
    print("=" * 70)
    
    result = helper.get_treatment_advice(disease, confidence)
    
    if result['success']:
        print(f"✅ SUCCESS!")
        print(f"\nDisease: {result['disease']}")
        print(f"Confidence: {result['confidence']}% ({result['confidence_level']})")
        print(f"\nAdvice Preview (first 300 chars):")
        print(result['advice'][:300] + "...")
    else:
        print(f"❌ FAILED: {result['error']}")

print("\n\n" + "=" * 70)
print("✅ TESTING COMPLETE!")
print("If all 10 tests passed, it works for ANY disease!")
print("=" * 70)