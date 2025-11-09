"""
Simple test to see doctor list clearly
"""

from skin_disease_helper import SkinDiseaseHelper

helper = SkinDiseaseHelper()

print("Finding dermatologists in Mysuru, Karnataka...")
print("=" * 70)

result = helper.find_doctors("Mysuru, Karnataka", radius_km=10, max_results=5)

if result['success']:
    print(f"\n✅ Found {result['doctors_found']} doctors (sorted by rating):\n")
    
    for i, doc in enumerate(result['doctors'], 1):
        print(f"{i}. {doc['name']}")
        print(f"   Rating: {doc['rating']} ⭐ ({doc['total_ratings']} reviews)")
        print(f"   Address: {doc['address']}")
        if doc['phone'] != 'N/A':
            print(f"   Phone: {doc['phone']}")
        if doc['website'] != 'N/A':
            print(f"   Website: {doc['website']}")
        print()
else:
    print(f"❌ Error: {result['error']}")