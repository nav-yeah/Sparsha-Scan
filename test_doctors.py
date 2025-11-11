"""
Simple test to see doctor list clearly
"""

from skin_disease_helper import SkinDiseaseHelper

helper = SkinDiseaseHelper()

print("Finding healthcare facilities (doctors/clinics) in Mysuru, Karnataka...")
print("=" * 70)

# The Geoapify implementation uses 'healthcare.doctor,healthcare.clinic' categories
result = helper.find_doctors("Mysuru, Karnataka", radius_km=10, max_results=5)

if result['success']:
    # Adjusted print message to reflect no sorting and the general category
    print(f"\n✅ Found {result['doctors_found']} facilities (sorted by distance):\n") 
    
    for i, doc in enumerate(result['doctors'], 1):
        print(f"{i}. {doc['name']}")
        
        # --- CHANGES HERE ---
        # The Geoapify data will return 'N/A' for rating/reviews.
        # We print them to confirm, but they won't show real values.
        print(f"   Rating: {doc['rating']} ({doc['total_ratings']} reviews) ⚠️") 
        # --------------------
        
        print(f"   Address: {doc['address']}")
        if doc['phone'] != 'N/A':
            print(f"   Phone: {doc['phone']}")
        if doc['website'] != 'N/A':
            print(f"   Website: {doc['website']}")
        print()
else:
    print(f"❌ Error: {result['error']}")
