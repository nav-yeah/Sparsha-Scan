import requests
import os
from typing import Optional, Dict

class WeatherService:
    """
    Service to fetch weather data for location-based skincare recommendations
    Uses OpenWeatherMap API (free tier available)
    """
    
    def __init__(self):
        # Get API key from environment or use a default
        self.api_key = os.getenv("OPENWEATHER_API_KEY", "")
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    def get_weather(self, location: str) -> Optional[Dict]:
        """
        Get weather data for a given location
        
        Args:
            location: City name or "city,country" format
            
        Returns:
            Dictionary with weather data including temperature, humidity, UV index
        """
        if not self.api_key:
            print(f"[Weather] No API key configured. Using mock data for {location}")
            # Return mock data if API key not configured
            return self._get_mock_weather(location)
        
        try:
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric"
            }
            
            print(f"[Weather] Fetching weather for: {location}")
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                weather_result = {
                    "temperature": round(data["main"]["temp"], 1),
                    "humidity": data["main"]["humidity"],
                    "condition": data["weather"][0]["main"],
                    "description": data["weather"][0]["description"],
                    "location": f"{data.get('name', location)}, {data.get('sys', {}).get('country', '')}",
                    "uv_index": self._estimate_uv_index(data)
                }
                print(f"[Weather] Successfully fetched weather: {weather_result['temperature']}°C, {weather_result['condition']}")
                return weather_result
            else:
                # Log the error
                error_data = response.json() if response.content else {}
                error_msg = error_data.get("message", f"HTTP {response.status_code}")
                print(f"[Weather] API error for {location}: {error_msg}")
                return self._get_mock_weather(location)
                
        except requests.exceptions.RequestException as e:
            print(f"[Weather] Request error for {location}: {e}")
            return self._get_mock_weather(location)
        except Exception as e:
            print(f"[Weather] Unexpected error for {location}: {e}")
            return self._get_mock_weather(location)
    
    def _estimate_uv_index(self, weather_data: Dict) -> int:
        """
        Estimate UV index based on weather conditions
        This is a simplified estimation - real UV data requires separate API
        """
        condition = weather_data["weather"][0]["main"].lower()
        if "clear" in condition or "sun" in condition:
            return 7
        elif "cloud" in condition:
            return 4
        else:
            return 3
    
    def _get_mock_weather(self, location: str) -> Dict:
        """
        Return mock weather data when API is unavailable
        Uses location name to generate slightly varied mock data for testing
        """
        # Generate slightly varied mock data based on location hash
        # This helps verify that different locations are being processed
        location_hash = hash(location.lower()) % 100
        
        # Vary temperature between 15-30°C based on location
        base_temp = 20 + (location_hash % 15)
        
        # Vary humidity between 40-80%
        humidity = 50 + (location_hash % 30)
        
        # Vary UV index
        uv_index = 3 + (location_hash % 5)
        
        # Vary conditions
        conditions = ["Clear", "Clouds", "Partly Cloudy", "Sunny"]
        condition = conditions[location_hash % len(conditions)]
        
        return {
            "temperature": base_temp,
            "humidity": humidity,
            "uv_index": uv_index,
            "condition": condition,
            "location": location,
            "note": "Mock data - configure OPENWEATHER_API_KEY for real data"
        }

