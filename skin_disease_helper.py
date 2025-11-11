import os
import requests # NEW: Import the requests library
from dotenv import load_dotenv
from typing import Dict, List, Optional
import google.generativeai as genai

# Load environment variables
load_dotenv()

class SkinDiseaseHelper:
    
    def __init__(self):
        # Gemini API for treatment advice (KEY NAME KEPT AS IS)
        self.gemini_key = os.getenv("GOOGLE_API_KEY")
        if not self.gemini_key:
            raise ValueError("GOOGLE_API_KEY not found in .env file")
        
        genai.configure(api_key=self.gemini_key)
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        # --- GEOAPIFY SETUP (REPLACES GOOGLE MAPS) ---
        self.places_key = os.getenv("GOOGLE_PLACES_API") # CHANGED: Key name to what you saved
        self.GEOAPIFY_PLACES_URL = "https://api.geoapify.com/v2/places"
        self.GEOAPIFY_GEOCODE_URL = "https://api.geoapify.com/v1/geocode/search"
        
        if not self.places_key:
            print("⚠️ Warning: GOOGLE_PLACES_API not found. Doctor search disabled.")
            
    # ... (get_treatment_advice function remains unchanged) ...
    def get_treatment_advice(
        self, 
        disease_name: str, 
        confidence_score: float
    ) -> Dict:
        # ... (Same code as original) ...
        # (Function omitted for brevity, it remains the same)
        # ...
        pass # Placeholder for the original code
    
    def _geocode_location(self, location_name: str) -> Optional[Dict]:
        """Converts location name (e.g., 'Mysuru, Karnataka') to coordinates."""
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
                coords = data['features'][0]['geometry']['coordinates']
                return {'lat': coords[1], 'lon': coords[0]}
            
        except Exception as e:
            print(f"Geocoding Error: {e}")
        return None


    def find_doctors(
        self, 
        location: str, 
        radius_km: float = 5.0,
        max_results: int = 5 # Used as the 'limit' parameter for Geoapify
    ) -> Dict:
        
        if not self.places_key: # Check for the Geoapify key
            return {
                "success": False,
                "error": "Doctor search not configured. Add GOOGLE_PLACES_API to .env file.",
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
                'filter': f'circle:{coords["lon"]},{coords["lat"]},{int(radius_km * 1000)}',
                'limit': max_results, # Use max_results as the limit
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
                    # Geoapify's free tier does NOT provide ratings/reviews, so we use N/A
                    "rating": 'N/A', 
                    "total_ratings": 'N/A',
                    "phone": props.get('datasource', {}).get('raw', {}).get('phone', 'N/A'),
                    "website": props.get('datasource', {}).get('raw', {}).get('website', 'N/A'),
                }
                
                doctors.append(doctor_info)
            
            # Note: No sorting needed, as ratings are not available. Results are returned by relevance/distance.
            
            return {
                "success": True,
                "location": location,
                "doctors_found": len(doctors),
                "doctors": doctors
            }
            
        except requests.exceptions.HTTPError as e:
            # Handle specific API errors (e.g., 401 unauthorized, 429 quota exceeded)
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
    
    # ... (complete_analysis function remains unchanged) ...
    def complete_analysis(
        self,
        disease_name: str,
        confidence_score: float,
        user_location: Optional[str] = None
    ) -> Dict:
        # ... (Same code as original) ...
        # (Function omitted for brevity, it remains the same)
        # ...
        pass # Placeholder for the original code

# ====================
# DEMO / TEST FUNCTION (REMAINS ALMOST UNCHANGED)
# ====================

def demo():
    # ... (Original demo code) ...
    pass # Placeholder for the original code
