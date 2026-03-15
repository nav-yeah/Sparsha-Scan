import os
import requests # NEW: Import the requests library for Geoapify
from dotenv import load_dotenv
from typing import Dict, List, Optional
import google.generativeai as genai

# Load environment variables
load_dotenv()


class SkinDiseaseHelper:
    
    def __init__(self):
        # 1. FIX: Load the correct key name for the Gemini API
        self.gemini_key = os.getenv("GOOGLE_API_KEY")
        if not self.gemini_key:
            # Change exception message to reflect the correct key name
            raise ValueError("GOOGLE_API_KEY not found in .env file")
        
        genai.configure(api_key=self.gemini_key)
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        # --- GEOAPIFY SETUP (REPLACES GOOGLE MAPS) ---
        # 2. Key name is correct here: GOOGLE_PLACES_API_KEY
        self.places_key = os.getenv("GOOGLE_PLACES_API_KEY") 
        self.GEOAPIFY_PLACES_URL = "https://api.geoapify.com/v2/places"
        self.GEOAPIFY_GEOCODE_URL = "https://api.geoapify.com/v1/geocode/search"
        
        if not self.places_key:
            # Change warning message to reflect the key being used
            print("⚠️ Warning: GOOGLE_PLACES_API_KEY not found. Doctor search disabled.")
            
    def get_treatment_advice(
        self, 
        disease_name: str, 
        confidence_score: float
    ) -> Dict:
        # ... (Gemini API logic remains correctly implemented) ...
        
        # Determine confidence level
        if confidence_score < 70:
            confidence_level = "LOW"
            urgency = "The detection confidence is low. Professional diagnosis is essential."
        elif confidence_score < 85:
            confidence_level = "MODERATE"
            urgency = "A dermatologist should confirm this diagnosis."
        else:
            confidence_level = "HIGH"
            urgency = "The detection confidence is good, but professional confirmation is recommended."
        
        prompt = f"""You are a medical information assistant. An AI detected a skin condition.

DETECTED CONDITION: {disease_name}
CONFIDENCE: {confidence_score}% ({confidence_level})
NOTE: {urgency}

Provide:
- What is {disease_name}?
- How common is it?

- Over-the-counter options
- Prescription treatments
- Home care tips
- Lifestyle changes

- Warning signs
- Urgency indicators

- What helps
- What to avoid

Keep it 250-300 words, simple language."""

        try:
            response = self.model.generate_content(prompt)
            advice = response.text
            
            disclaimer = (
                "\n\n⚠️ DISCLAIMER: This is educational information only. "
                "Always consult a dermatologist for proper diagnosis and treatment."
            )
            
            return {
                "success": True,
                "disease": disease_name,
                "confidence": confidence_score,
                "confidence_level": confidence_level,
                "advice": advice + disclaimer,
                "recommend_urgent_care": confidence_score < 70
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "advice": "Unable to generate advice. Please consult a dermatologist."
            }
            
    # NEW HELPER FUNCTION: Replaces Google Maps geocoding
    def _geocode_location(self, location_name: str) -> Optional[Dict]:
        """Converts location name (e.g., 'Mysuru, Karnataka') to coordinates using Geoapify."""
        if not self.places_key:
            return None
        
        try:
            params = {
                'text': location_name,
                'apiKey': self.places_key,
                'limit': 1
            }
            response = requests.get(self.GEOAPIFY_GEOCODE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data and data.get('features'):
                # Geoapify returns [lon, lat], we store {'lat', 'lon'}
                coords = data['features'][0]['geometry']['coordinates']
                return {'lat': coords[1], 'lon': coords[0]}
            
        except Exception as e:
            print(f"Geocoding Error: {e}")
        return None


    # FULLY REPLACED FUNCTION: Uses Geoapify for doctor search
    def find_doctors(
        self, 
        location: str, 
        radius_km: float = 5.0,
        max_results: int = 5 
    ) -> Dict:
        
        if not self.places_key:
            return {
                "success": False,
                "error": "Doctor search not configured. Add GOOGLE_PLACES_API_KEY to .env file.",
                "doctors": []
            }
        
        # 1. Convert user's location to Lat/Lon coordinates
        coords = self._geocode_location(location)
        if not coords:
             return {
                "success": False,
                "error": f"Could not find coordinates for location: {location}",
                "doctors": []
            }
            
        try:
            # 2. Use Geoapify Places API to search around the coordinates
            places_params = {
                'categories': 'healthcare.doctor,healthcare.clinic', # Targeted search
                # 3. FIX: Swapped coordinates to Lat, Lon to solve the 400 Bad Request error
                'filter': f'circle:{coords["lat"]},{coords["lon"]},{int(radius_km * 1000)}',
                'limit': max_results,
                'apiKey': self.places_key
            }
            
            response = requests.get(self.GEOAPIFY_PLACES_URL, params=places_params)
            response.raise_for_status()
            places_data = response.json()
            
            doctors = []
            for feature in places_data.get('features', []):
                props = feature['properties']
                addr_line2 = props.get('address_line2', '')
                
                doctor_info = {
                    "name": props.get('name', 'N/A'),
                    "address": f"{props.get('address_line1', '')}, {addr_line2}".strip(', '),
                    # Geoapify does not provide public ratings/reviews
                    "rating": 'N/A', 
                    "total_ratings": 'N/A',
                    "phone": props.get('datasource', {}).get('raw', {}).get('phone', 'N/A'),
                    "website": props.get('datasource', {}).get('raw', {}).get('website', 'N/A'),
                }
                
                doctors.append(doctor_info)
            
            # Note: Sorting by rating is removed as ratings are not available.
            
            return {
                "success": True,
                "location": location,
                "doctors_found": len(doctors),
                "doctors": doctors
            }
            
        except requests.exceptions.HTTPError as e:
            return {
                "success": False,
                "error": f"API Request Failed (HTTP Error): {e}",
                "doctors": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "doctors": []
            }
    
    def complete_analysis(
        self,
        disease_name: str,
        confidence_score: float,
        user_location: Optional[str] = None
    ) -> Dict: #Function to be called to integrate into main program
        
        # Get treatment advice
        treatment = self.get_treatment_advice(disease_name, confidence_score)
        
        # Find nearby doctors if location provided
        doctors = {"doctors": []}
        if user_location:
            doctors = self.find_doctors(user_location)
        
        return {
            "disease_detection": {
                "disease": disease_name,
                "confidence": confidence_score
            },
            "treatment_advice": treatment,
            "nearby_doctors": doctors
        }


# ====================
# DEMO / TEST FUNCTION
# ====================

def demo():
    print("=" * 70)
    print("SKIN DISEASE HELPER - COMPLETE DEMO")
    print("=" * 70)
    
    # Initialize helper
    helper = SkinDiseaseHelper()
    
    # Example 1: Just treatment advice (no location)
    print("\n\n📋 EXAMPLE 1: Treatment Advice Only")
    print("-" * 70)
    print("Simulating: ML model detected 'Eczema' with 89.5% confidence")
    print()
    
    result = helper.complete_analysis(
        disease_name="Eczema",
        confidence_score=89.5
    )
    
    print(f"Disease: {result['disease_detection']['disease']}")
    print(f"Confidence: {result['disease_detection']['confidence']}%")
    print(f"\nTreatment Advice:")
    print(result['treatment_advice']['advice'])
    
    # Example 2: With doctor recommendations
    print("\n\n📋 EXAMPLE 2: Treatment + Doctor Recommendations (Using Geoapify)")
    print("-" * 70)
    print("Simulating: ML model detected 'Psoriasis' with 78% confidence")
    print("User location: Mysuru, Karnataka")
    print()
    
    result = helper.complete_analysis(
        disease_name="Psoriasis",
        confidence_score=78.0,
        user_location="Mysuru, Karnataka"
    )
    
    print(f"Disease: {result['disease_detection']['disease']}")
    print(f"Confidence: {result['disease_detection']['confidence']}%")
    print(f"\nTreatment Advice:")
    print(result['treatment_advice']['advice'][:500] + "...")  # Truncated for demo
    
    if result['nearby_doctors']['success']:
        print(f"\n\n👨‍⚕️ Found {result['nearby_doctors']['doctors_found']} Dermatologists (Note: No Ratings from Geoapify):")
        for i, doc in enumerate(result['nearby_doctors']['doctors'], 1):
            print(f"\n{i}. {doc['name']}")
            print(f"   Address: {doc['address']}")
            print(f"   Rating: {doc['rating']} ⭐ ({doc['total_ratings']} reviews)")
            if doc.get('phone') != 'N/A':
                print(f"   Phone: {doc['phone']}")
    else:
        print(f"\n\n🚨 Doctor Search Failed: {result['nearby_doctors']['error']}")
    
    print("\n\n" + "=" * 70)
    print("✅ DEMO COMPLETE")
    print("=" * 70)


# ==================================
# HOW YOUR TEAMMATES SHOULD USE THIS
# ==================================

def integration_example():
    """
    Show teammates exactly how to integrate with their ML model
    """
    print("""
    
HOW TO INTEGRATE WITH YOUR ML MODEL:
====================================

# In your main ML prediction file:

from skin_disease_helper import SkinDiseaseHelper

# Initialize once
helper = SkinDiseaseHelper()

# After ML model predicts:
ml_prediction = your_model.predict(image)  
# Returns something like: {"disease": "Eczema", "confidence": 89.5}

# Get complete information:
result = helper.complete_analysis(
    disease_name=ml_prediction['disease'],
    confidence_score=ml_prediction['confidence'],
    user_location="Bangalore, Karnataka"  # Optional
)

# Use the results:
print(result['treatment_advice']['advice'])
print(result['nearby_doctors']['doctors'])

    """)


if __name__ == "__main__":
    demo()
    integration_example()
