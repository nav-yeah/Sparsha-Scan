"""
Complete Skin Disease Helper Module
Provides treatment advice + doctor recommendations
"""

import google.generativeai as genai
import googlemaps
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional

# Load environment variables
load_dotenv()


class SkinDiseaseHelper:
    """
    Complete helper for skin disease detection system.
    Your teammates can use this by just passing disease name and location.
    """
    
    def __init__(self):
        """Initialize with API keys from .env file"""
        # Gemini API for treatment advice
        self.gemini_key = os.getenv("GOOGLE_API_KEY")
        self.model = None
        
        if self.gemini_key:
            try:
                genai.configure(api_key=self.gemini_key)
                self.model = genai.GenerativeModel('models/gemini-2.5-flash')
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize Gemini API: {e}")
                self.model = None
        else:
            print("⚠️ Warning: GOOGLE_API_KEY not found in .env file. Treatment advice will use fallback.")
        
        # Google Maps API for doctor search
        self.places_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if self.places_key:
            try:
                self.gmaps = googlemaps.Client(key=self.places_key)
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize Google Maps API: {e}")
                self.gmaps = None
        else:
            self.gmaps = None
            print("⚠️ Warning: GOOGLE_PLACES_API_KEY not found. Doctor search disabled.")
    
    def get_treatment_advice(
        self, 
        disease_name: str, 
        confidence_score: float
    ) -> Dict:
        """
        Get treatment advice for detected skin disease.
        
        Args:
            disease_name: Disease detected by ML model (e.g., "Eczema")
            confidence_score: Confidence percentage (0-100)
            
        Returns:
            Dictionary with treatment advice
        """
        
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

Provide treatment advice in JSON format only. Use this exact structure:

{{
  "about": {{
    "description": "Brief 2-3 sentence description of what {disease_name} is",
    "commonality": "Brief 1-2 sentence about how common it is"
  }},
  "treatment_options": {{
    "over_the_counter": ["Option 1", "Option 2", "Option 3"],
    "prescription": ["Option 1", "Option 2"],
    "home_care": ["Tip 1", "Tip 2", "Tip 3"],
    "lifestyle": ["Change 1", "Change 2"]
  }},
  "when_to_see_doctor": {{
    "warning_signs": ["Sign 1", "Sign 2", "Sign 3"],
    "urgency": "Brief sentence about when to seek immediate care"
  }},
  "dos_and_donts": {{
    "dos": ["Do this", "Do that", "Do something else"],
    "donts": ["Don't do this", "Don't do that", "Avoid this"]
  }}
}}

Important:
- Return ONLY valid JSON, no markdown, no explanations, no code blocks
- Use simple, clear language
- Keep each item concise (1 short sentence or phrase)
- All arrays should have 2-4 items
- Do not include any text before or after the JSON"""

        # If model is not available, return fallback advice
        if not self.model:
            return {
                "success": True,
                "disease": disease_name,
                "confidence": confidence_score,
                "confidence_level": confidence_level,
                "advice": f"Based on the detection of {disease_name} with {confidence_score}% confidence, it is recommended to consult with a dermatologist for proper diagnosis and treatment. The confidence level is {confidence_level.lower()}, so professional medical advice is essential.",
                "recommend_urgent_care": confidence_score < 70
            }
        
        try:
            print(f"   Sending prompt to Gemini API...")
            response = self.model.generate_content(prompt)
            
            # Extract text from response - handle different response formats
            if hasattr(response, 'text'):
                advice_text = response.text
            elif hasattr(response, 'candidates') and len(response.candidates) > 0:
                advice_text = response.candidates[0].content.parts[0].text
            else:
                # Try to get text from response object
                advice_text = str(response)
            
            if not advice_text or len(advice_text.strip()) == 0:
                raise ValueError("Empty response from Gemini API")
            
            print(f"   ✅ Received {len(advice_text)} characters from Gemini API")
            
            # Clean the response - remove markdown code blocks if present
            advice_text = advice_text.strip()
            if advice_text.startswith('```json'):
                advice_text = advice_text[7:]  # Remove ```json
            if advice_text.startswith('```'):
                advice_text = advice_text[3:]  # Remove ```
            if advice_text.endswith('```'):
                advice_text = advice_text[:-3]  # Remove trailing ```
            advice_text = advice_text.strip()
            
            # Parse JSON
            try:
                import json
                advice_json = json.loads(advice_text)
                print(f"   ✅ Successfully parsed JSON response")
            except json.JSONDecodeError as json_err:
                print(f"   ⚠️ Failed to parse JSON: {json_err}")
                print(f"   Response text: {advice_text[:200]}...")
                raise ValueError(f"Invalid JSON response from Gemini API: {json_err}")
            
            # Validate JSON structure
            required_keys = ['about', 'treatment_options', 'when_to_see_doctor', 'dos_and_donts']
            for key in required_keys:
                if key not in advice_json:
                    raise ValueError(f"Missing required key in JSON: {key}")
            
            return {
                "success": True,
                "disease": disease_name,
                "confidence": confidence_score,
                "confidence_level": confidence_level,
                "advice": advice_json,  # Return structured JSON instead of text
                "recommend_urgent_care": confidence_score < 70
            }
            
        except Exception as e:
            print(f"❌ Error generating treatment advice from Gemini API: {e}")
            import traceback
            traceback.print_exc()
            # Return fallback advice but mark as unsuccessful
            return {
                "success": False,
                "error": str(e),
                "disease": disease_name,
                "confidence": confidence_score,
                "confidence_level": confidence_level,
                "advice": None,
                "recommend_urgent_care": confidence_score < 70
            }
    
    def find_doctors(
        self, 
        location: str, 
        radius_km: float = 5.0,
        max_results: int = 5
    ) -> Dict:
        """
        Find dermatologists near given location, sorted by rating.
        
        Args:
            location: City name or address (e.g., "Mysuru" or "Bangalore, Karnataka")
            radius_km: Search radius in kilometers (default: 5km)
            max_results: Maximum number of doctors to return (default: 5)
            
        Returns:
            Dictionary with list of doctors sorted by rating (highest first)
        """
        
        if not self.gmaps:
            return {
                "success": False,
                "error": "Doctor search not configured. Add GOOGLE_PLACES_API_KEY to .env file.",
                "doctors": []
            }
        
        try:
            # Check if location is coordinates (lat,lng format)
            is_coordinates = ',' in location and len(location.split(',')) == 2
            
            if is_coordinates:
                # Use coordinates for nearby search
                try:
                    lat, lng = map(float, location.split(','))
                    places_result = self.gmaps.places_nearby(
                        location=(lat, lng),
                        radius=int(radius_km * 1000),  # Convert km to meters
                        type='doctor',
                        keyword='dermatologist'
                    )
                except ValueError:
                    # If coordinates are invalid, fall back to text search
                    places_result = self.gmaps.places(
                        query=f"dermatologist near {location}",
                        radius=int(radius_km * 1000)
                    )
            else:
                # Use text search for city/address
                places_result = self.gmaps.places(
                    query=f"dermatologist in {location}",
                    radius=int(radius_km * 1000)  # Convert km to meters
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