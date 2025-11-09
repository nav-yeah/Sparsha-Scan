

import google.generativeai as genai
import googlemaps
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional

# Load environment variables
load_dotenv()


class SkinDiseaseHelper:
    
    def __init__(self):
        # Gemini API for treatment advice
        self.gemini_key = os.getenv("GOOGLE_API_KEY")
        if not self.gemini_key:
            raise ValueError("GOOGLE_API_KEY not found in .env file")
        
        genai.configure(api_key=self.gemini_key)
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        # Google Maps API for doctor search
        self.places_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if self.places_key:
            self.gmaps = googlemaps.Client(key=self.places_key)
        else:
            self.gmaps = None
            print("⚠️ Warning: GOOGLE_PLACES_API_KEY not found. Doctor search disabled.")
    
    def get_treatment_advice(
        self, 
        disease_name: str, 
        confidence_score: float
    ) -> Dict:
        
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
    
    def find_doctors(
        self, 
        location: str, 
        radius_km: float = 5.0,
        max_results: int = 5
    ) -> Dict:
        
        if not self.gmaps:
            return {
                "success": False,
                "error": "Doctor search not configured. Add GOOGLE_PLACES_API_KEY to .env file.",
                "doctors": []
            }
        
        try:
            # Search for dermatologists
            places_result = self.gmaps.places(
                query=f"dermatologist in {location}",
                radius=radius_km * 1000  # Convert km to meters
            )
            
            doctors = []
            for place in places_result.get('results', []):
                doctor_info = {
                    "name": place.get('name', 'N/A'),
                    "address": place.get('formatted_address', 'N/A'),
                    "rating": place.get('rating', 0),  # Default to 0 if no rating
                    "total_ratings": place.get('user_ratings_total', 0),
                }
                
                # Add phone if available
                if 'place_id' in place:
                    try:
                        details = self.gmaps.place(place['place_id'])
                        result = details.get('result', {})
                        doctor_info['phone'] = result.get('formatted_phone_number', 'N/A')
                        doctor_info['website'] = result.get('website', 'N/A')
                    except:
                        doctor_info['phone'] = 'N/A'
                        doctor_info['website'] = 'N/A'
                
                doctors.append(doctor_info)
            
            # Sort by rating (highest first), then by number of reviews
            doctors.sort(key=lambda x: (x['rating'], x['total_ratings']), reverse=True)
            
            # Return only the top max_results
            doctors = doctors[:max_results]
            
            return {
                "success": True,
                "location": location,
                "doctors_found": len(doctors),
                "doctors": doctors
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
    print("\n\n📋 EXAMPLE 2: Treatment + Doctor Recommendations")
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
        print(f"\n\n👨‍⚕️ Found {result['nearby_doctors']['doctors_found']} Dermatologists:")
        for i, doc in enumerate(result['nearby_doctors']['doctors'], 1):
            print(f"\n{i}. {doc['name']}")
            print(f"   Address: {doc['address']}")
            print(f"   Rating: {doc['rating']} ⭐ ({doc['total_ratings']} reviews)")
            if doc.get('phone') != 'N/A':
                print(f"   Phone: {doc['phone']}")
    
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