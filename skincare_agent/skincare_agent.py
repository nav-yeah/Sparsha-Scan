from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import os
from typing import Dict, Any

class SkincareAgent:
    """
    LangChain-based agent for generating personalized skincare recommendations
    Uses weighted context system (Skin Type 40%, Weather 30%, Occupation 20%, Age 10%)
    """
    
    def __init__(self):
        # Initialize LLM - defaults to OpenAI, but can use other providers
        api_key = os.getenv("OPENAI_API_KEY", "")
        if api_key:
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.9,  # Higher temperature for more variation
                api_key=api_key
            )
        else:
            self.llm = None
            print("OPENAI_API_KEY not set. Using fallback recommendations.")
    
    def _build_weighted_context(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build weighted context system for personalized recommendations
        
        Weights:
        - Skin Type: 40% (most important)
        - Weather: 30% (second most important)
        - Occupation: 20% (third most important)
        - Age: 10% (optional)
        
        Returns structured context with weights and detailed analysis
        """
        skin_type = user_info.get("skin_type", "normal")
        occupation = user_info.get("occupation", "")
        location = user_info.get("location", "")
        age = user_info.get("age")
        weather = user_info.get("weather", {})
        
        # Build weighted context
        context = {
            "primary_factors": {
                "skin_type": {
                    "value": skin_type,
                    "weight": 40,
                    "priority": "CRITICAL",
                    "analysis": self._analyze_skin_type(skin_type)
                },
                "weather": {
                    "value": weather,
                    "weight": 30,
                    "priority": "HIGH",
                    "analysis": self._analyze_weather(weather)
                },
                "occupation": {
                    "value": occupation,
                    "weight": 20,
                    "priority": "MEDIUM",
                    "analysis": self._analyze_occupation(occupation)
                }
            },
            "secondary_factors": {}
        }
        
        if age:
            context["secondary_factors"]["age"] = {
                "value": age,
                "weight": 10,
                "priority": "LOW",
                "analysis": self._analyze_age(age)
            }
        
        context["location"] = location
        
        return context
    
    def _analyze_skin_type(self, skin_type: str) -> str:
        """Analyze skin type and provide specific considerations"""
        analyses = {
            "oily": "Oily skin requires oil-control, pore-minimizing products. Focus on lightweight, non-comedogenic formulations. May need more frequent cleansing but avoid over-stripping. Salicylic acid and niacinamide are beneficial.",
            "dry": "Dry skin needs intensive hydration and barrier repair. Rich, emollient products with ceramides, hyaluronic acid, and occlusives are essential. Avoid harsh cleansers and alcohol-based products.",
            "normal": "Normal skin can tolerate a balanced routine. Focus on maintenance, prevention, and gentle care. Can experiment with various product types but should maintain consistency."
        }
        return analyses.get(skin_type.lower(), analyses["normal"])
    
    def _analyze_weather(self, weather: Dict) -> str:
        """Analyze weather conditions and their impact on skin"""
        if not weather:
            return "Weather data not available. Use general recommendations."
        
        temp = weather.get("temperature", 20)
        humidity = weather.get("humidity", 50)
        uv_index = weather.get("uv_index", 5)
        condition = weather.get("condition", "Unknown")
        
        analysis_parts = []
        
        # Temperature analysis
        if temp > 28:
            analysis_parts.append(f"Hot climate ({temp}°C): Skin may produce more oil, sweat more. Lighter products, frequent cleansing, and hydration are key.")
        elif temp < 10:
            analysis_parts.append(f"Cold climate ({temp}°C): Skin barrier may be compromised. Richer moisturizers, barrier repair products, and protection from wind are essential.")
        else:
            analysis_parts.append(f"Moderate temperature ({temp}°C): Standard skincare routine should work well.")
        
        # Humidity analysis
        if humidity < 40:
            analysis_parts.append(f"Low humidity ({humidity}%): Skin loses moisture faster. Increase hydration, use humectants, and consider humidifiers.")
        elif humidity > 70:
            analysis_parts.append(f"High humidity ({humidity}%): May feel sticky, products may not absorb well. Lighter formulations, gel-based products work better.")
        else:
            analysis_parts.append(f"Moderate humidity ({humidity}%): Balanced environment for skin.")
        
        # UV analysis
        if uv_index >= 7:
            analysis_parts.append(f"Very high UV index ({uv_index}): Critical sun protection needed. SPF 50+, reapplication every 2 hours, physical barriers (hats, clothing).")
        elif uv_index >= 5:
            analysis_parts.append(f"High UV index ({uv_index}): Strong sun protection required. SPF 30-50, regular reapplication.")
        else:
            analysis_parts.append(f"Moderate UV index ({uv_index}): Standard SPF 30 protection sufficient.")
        
        # Condition analysis
        if "rain" in condition.lower() or "cloud" in condition.lower():
            analysis_parts.append("Cloudy/rainy conditions: Still need UV protection as UV rays penetrate clouds.")
        
        return " ".join(analysis_parts)
    
    def _analyze_occupation(self, occupation: str) -> str:
        """Analyze occupation and its impact on skincare needs"""
        if not occupation:
            return "Occupation not specified. Use general lifestyle recommendations."
        
        occupation_lower = occupation.lower()
        
        # Indoor/office jobs
        if any(word in occupation_lower for word in ["engineer", "developer", "programmer", "designer", "office", "desk", "admin", "manager", "analyst"]):
            return "Indoor/office work: Prolonged screen time may cause eye strain and blue light exposure. Air conditioning can dry skin. Focus on hydration, eye care, and regular breaks."
        
        # Outdoor jobs
        elif any(word in occupation_lower for word in ["construction", "outdoor", "field", "delivery", "driver", "farming", "gardening"]):
            return "Outdoor work: High sun exposure, pollution, and environmental stressors. Emphasize strong sun protection, antioxidant serums, and barrier repair. Post-work cleansing is crucial."
        
        # Healthcare
        elif any(word in occupation_lower for word in ["doctor", "nurse", "medical", "healthcare", "hospital"]):
            return "Healthcare work: Frequent hand washing, mask-wearing, and stress can affect skin. Focus on barrier repair, gentle cleansing, and stress management for skin health."
        
        # Creative/beauty
        elif any(word in occupation_lower for word in ["makeup", "beauty", "stylist", "photographer", "model"]):
            return "Beauty/creative work: Frequent product use and makeup may require double cleansing and skin barrier support. Regular skin detox days recommended."
        
        # Service industry
        elif any(word in occupation_lower for word in ["server", "waiter", "retail", "sales", "customer service"]):
            return "Service industry: Variable environments, stress, and irregular schedules. Focus on adaptable routine, stress management, and consistent basics."
        
        # Education
        elif any(word in occupation_lower for word in ["teacher", "professor", "educator", "student"]):
            return "Education: Stress, long hours, and exposure to various environments. Focus on stress management, consistent routine, and protective products."
        
        else:
            return f"Occupation: {occupation}. Consider work environment (indoor/outdoor), stress levels, and schedule when recommending skincare routine."
    
    def _analyze_age(self, age: int) -> str:
        """Analyze age and its impact on skincare needs"""
        if age < 20:
            return "Teenage/young adult: Focus on prevention, gentle products, and establishing good habits. May need acne management if applicable."
        elif age < 30:
            return "Young adult: Prevention is key. Focus on antioxidants, SPF, and establishing consistent routine. Early anti-aging can begin."
        elif age < 40:
            return "Adult: Begin incorporating anti-aging ingredients (retinoids, peptides). Maintain hydration and sun protection. Address early signs of aging."
        elif age < 50:
            return "Mature adult: Increased focus on anti-aging, collagen support, and barrier repair. May need richer formulations and targeted treatments."
        else:
            return "Mature skin: Emphasize barrier repair, hydration, and anti-aging. Richer products, gentle exfoliation, and professional treatments may be beneficial."
    
    async def get_recommendations(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized skincare recommendations using LangChain with weighted context
        
        Args:
            user_info: Dictionary containing skin_type, occupation, location, age, weather
            
        Returns:
            Dictionary with personalized recommendations
        """
        if not self.llm:
            # Fallback recommendations without AI
            print("[AI Agent] ⚠️ WARNING: OpenAI API key not set! Using fallback recommendations.")
            print("[AI Agent] To get AI-powered personalized recommendations, set OPENAI_API_KEY in .env file")
            return self._get_fallback_recommendations(user_info)
        
        try:
            # Build weighted context
            weighted_context = self._build_weighted_context(user_info)
            
            # Debug: Print context being sent
            print(f"[AI Agent] Processing request for:")
            print(f"  Skin Type: {user_info.get('skin_type')}")
            print(f"  Occupation: {user_info.get('occupation')}")
            print(f"  Location: {user_info.get('location')}")
            print(f"  Weather: {user_info.get('weather')}")
            print(f"  Age: {user_info.get('age')}")
            
            # Use LangChain directly for better control
            result_str = await self._langchain_call(weighted_context, user_info)
            
            print(f"[AI Agent] Response received (first 300 chars): {result_str[:300]}...")
            
            return {
                "recommendations": result_str,
                "skin_type": user_info.get("skin_type", "normal"),
                "personalized": True
            }
            
        except Exception as e:
            print(f"[AI Agent] Error: {e}")
            import traceback
            traceback.print_exc()
            return self._get_fallback_recommendations(user_info)
    
    def _build_task_description(self, weighted_context: Dict[str, Any], user_info: Dict[str, Any]) -> str:
        """Build detailed task description with weighted context reasoning"""
        
        primary = weighted_context["primary_factors"]
        secondary = weighted_context.get("secondary_factors", {})
        location = weighted_context.get("location", "")
        
        task = f"""You are creating a UNIQUE, PERSONALIZED skincare recommendation. 

🚨 CRITICAL: You MUST give DIFFERENT recommendations for the SAME skin type when other factors change.

COMPARISON EXAMPLES - SAME SKIN TYPE, DIFFERENT FACTORS = DIFFERENT RECOMMENDATIONS:

Example 1A - Oily Skin + Hot Weather (35°C) + Construction Worker:
Morning: Pre-work oil-control cleanser with salicylic acid → Lightweight gel moisturizer → SPF 50+ mineral sunscreen → Mattifying primer
Evening: Post-work double cleanse → Clay mask (2x/week) → Niacinamide serum → Lightweight gel moisturizer
Reasoning: Hot weather increases oil production, construction work adds dirt/pollution, needs maximum sun protection

Example 1B - Oily Skin + Cold Weather (5°C) + Office Worker:
Morning: Gentle foaming cleanser → Hydrating toner → Lightweight but hydrating moisturizer → SPF 30+ 
Evening: Oil-based cleanser → Salicylic acid treatment (3x/week) → Barrier-supporting moisturizer
Reasoning: Cold weather can dry skin even if oily, office AC is drying, less sun exposure needed

Example 2A - Normal Skin + Hot Humid (30°C, 80% humidity) + Healthcare Worker:
Morning: Gel cleanser → Lightweight serum → Oil-free gel moisturizer → SPF 50+ → Barrier cream for mask area
Evening: Micellar water for mask area → Gentle cleanser → Antioxidant serum → Lightweight moisturizer
Reasoning: High humidity makes products feel sticky, healthcare workers need mask-friendly products

Example 2B - Normal Skin + Cold Dry (2°C, 30% humidity) + Software Engineer:
Morning: Cream cleanser → Hydrating serum → Rich moisturizer with ceramides → SPF 30+ → Eye cream
Evening: Gentle cleanser → Hyaluronic acid serum → Rich night cream → Eye treatment
Reasoning: Cold + dry air needs barrier protection, screen time needs eye care

⚠️ YOUR CURRENT TASK - MUST BE UNIQUE:
Skin Type: {primary['skin_type']['value']}
Weather: {user_info.get('weather', {}).get('temperature', 'N/A')}°C, {user_info.get('weather', {}).get('humidity', 'N/A')}% humidity, UV {user_info.get('weather', {}).get('uv_index', 'N/A')}
Occupation: {primary['occupation']['value']}
Age: {secondary.get('age', {}).get('value', 'Not specified') if secondary.get('age') else 'Not specified'}

❌ DO NOT give the same recommendations as Examples 1A, 1B, 2A, or 2B.
✅ Create NEW, UNIQUE recommendations that combine ALL these specific factors.
✅ If the skin type matches an example but weather/occupation is different, your recommendations MUST be different.

=== WEIGHTED CONTEXT SYSTEM ===

PRIMARY FACTOR 1 - SKIN TYPE (Weight: 40% - HIGHEST PRIORITY):
Value: {primary['skin_type']['value']}
Analysis: {primary['skin_type']['analysis']}

This is the MOST IMPORTANT factor. Base your core product recommendations on this, but then MODIFY them based on other factors.

PRIMARY FACTOR 2 - WEATHER CONDITIONS (Weight: 30% - SECOND PRIORITY):
Current Weather Data:
- Location: {location}
- Temperature: {user_info.get('weather', {}).get('temperature', 'N/A')}°C
- Humidity: {user_info.get('weather', {}).get('humidity', 'N/A')}%
- UV Index: {user_info.get('weather', {}).get('uv_index', 'N/A')}
- Condition: {user_info.get('weather', {}).get('condition', 'N/A')}

Weather Analysis: {primary['weather']['analysis']}

This significantly impacts product choices. For example:
- Hot + Oily skin = lighter, more mattifying products
- Cold + Dry skin = richer, more protective products
- High UV = stronger sun protection regardless of skin type
- Low humidity = more hydration needed

PRIMARY FACTOR 3 - OCCUPATION (Weight: 20% - THIRD PRIORITY):
Occupation: {primary['occupation']['value']}
Analysis: {primary['occupation']['analysis']}

This affects:
- Product application timing (AM/PM routines)
- Specific concerns (e.g., maskne for healthcare workers)
- Lifestyle adjustments needed

"""
        
        if secondary.get("age"):
            task += f"""
SECONDARY FACTOR - AGE (Weight: 10%):
Age: {secondary['age']['value']}
Analysis: {secondary['age']['analysis']}

This influences:
- Anti-aging product recommendations
- Product texture preferences
- Treatment intensity
"""
        
        task += f"""

=== YOUR TASK ===

Using REASONING, create a personalized skincare plan that:

1. **Morning Routine (AM)**: 
   - Start with skin type needs (40% weight)
   - Adjust for weather conditions (30% weight) - e.g., if hot/humid, use lighter products even for dry skin
   - Consider occupation needs (20% weight) - e.g., if outdoor work, emphasize sun protection
   - Factor in age if provided (10% weight)
   - Provide SPECIFIC product categories and WHY they're chosen for THIS combination

2. **Evening Routine (PM)**:
   - Same reasoning approach
   - Consider occupation schedule (e.g., night shift workers may need different timing)
   - Weather may affect evening routine (e.g., cold weather needs richer products at night)

3. **Product Recommendations**:
   - List SPECIFIC product categories (not just "moisturizer" but "lightweight gel moisturizer with hyaluronic acid for hot climate")
   - Explain WHY each product is recommended for THIS specific combination
   - Vary recommendations - someone with oily skin in hot weather needs different products than oily skin in cold weather

4. **Lifestyle Tips**:
   - Occupation-specific advice
   - Weather-adapted practices
   - Age-appropriate recommendations

5. **Weekly Treatments**:
   - Tailored to the combination of factors
   - E.g., oily skin in high humidity may need more frequent exfoliation

6. **Important Considerations**:
   - Address potential conflicts between factors
   - Provide warnings specific to this combination

=== REASONING REQUIREMENT ===

For EACH recommendation, you MUST explain how you weighed the factors:
- "Because this person has [skin type] in [weather condition] doing [occupation], I recommend [specific product] because..."

⚠️ MANDATORY UNIQUENESS TEST:
Before you write your response, answer these questions:

1. If I changed ONLY the weather (kept same skin type, occupation, age), would my recommendations change?
   → If NO, you're being generic. FIX IT by adding weather-specific products.

2. If I changed ONLY the occupation (kept same skin type, weather, age), would my recommendations change?
   → If NO, you're being generic. FIX IT by adding occupation-specific products.

3. If I changed ONLY the age (kept same skin type, weather, occupation), would my recommendations change?
   → If NO, you're being generic. FIX IT by adding age-appropriate products.

If ANY answer is NO, you MUST rewrite your recommendations to be more specific.

FOR THIS SPECIFIC COMBINATION:
- Skin Type: {primary['skin_type']['value']} (base 40%)
- Weather: {user_info.get('weather', {}).get('temperature', 'N/A')}°C, {user_info.get('weather', {}).get('humidity', 'N/A')}% (modify 30%)
- Occupation: {primary['occupation']['value']} (modify 20%)
- Age: {secondary.get('age', {}).get('value', 'N/A') if secondary.get('age') else 'N/A'} (modify 10%)

Your recommendations MUST show how you're modifying the base skin type routine based on weather, occupation, and age.

=== OUTPUT FORMAT ===

Format your response EXACTLY as follows:

**Morning Routine (AM):**
[Specific products with reasoning for THIS combination]

**Evening Routine (PM):**
[Specific products with reasoning for THIS combination]

**Product Recommendations:**
[Specific product categories with explanations - NOT generic lists]

**Lifestyle Tips:**
[Occupation and weather-specific advice]

**Weekly Treatments:**
[Specific to this combination]

**Important Considerations:**
[Warnings specific to this combination]

Remember: If I can swap out the weather/occupation/age and get the same recommendations, you've failed. Make it UNIQUE!
"""
        
        return task
    
    def _get_fallback_recommendations(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback recommendations when AI is not available
        Uses weighted context to provide personalized recommendations
        """
        # Build weighted context even for fallback
        weighted_context = self._build_weighted_context(user_info)
        
        skin_type = user_info.get("skin_type", "normal")
        weather = user_info.get("weather", {})
        occupation = user_info.get("occupation", "")
        age = user_info.get("age")
        
        # Get base routine and modify based on factors
        base_routine = self._get_routine_for_skin_type(skin_type)
        personalized_routine = self._personalize_routine(base_routine, weighted_context, user_info)
        
        base_products = self._get_products_for_skin_type(skin_type)
        personalized_products = self._personalize_products(base_products, weighted_context, user_info)
        
        # Format as string to match AI response format
        recommendations_text = self._format_fallback_as_text(
            skin_type, personalized_routine, personalized_products, 
            weather, occupation, age
        )
        
        recommendations = {
            "skin_type": skin_type,
            "personalized": False,
            "recommendations": recommendations_text,
            "daily_routine": personalized_routine,
            "product_recommendations": personalized_products,
            "weather_tips": self._get_weather_tips(weather),
            "lifestyle_tips": self._get_lifestyle_tips(occupation, weather, age),
            "note": "AI recommendations unavailable. Using weighted context-based fallback."
        }
        
        return recommendations
    
    def _format_fallback_as_text(self, skin_type: str, routine: Dict, products: list, 
                                  weather: Dict, occupation: str, age: int = None) -> str:
        """Format fallback recommendations as text similar to AI response"""
        text = f"""**Personalized Recommendations for {skin_type.capitalize()} Skin**

**Daily Routine**

**Morning:**
"""
        for item in routine["morning"]:
            text += f"- {item}\n"
        
        text += "\n**Evening:**\n"
        for item in routine["evening"]:
            text += f"- {item}\n"
        
        text += "\n**Product Recommendations:**\n"
        for item in products:
            text += f"- {item}\n"
        
        weather_tips = self._get_weather_tips(weather)
        if weather_tips:
            text += "\n**Weather Tips:**\n"
            for tip in weather_tips:
                text += f"- {tip}\n"
        
        lifestyle_tips = self._get_lifestyle_tips(occupation, weather, age)
        if lifestyle_tips:
            text += "\n**Lifestyle Tips:**\n"
            for tip in lifestyle_tips:
                text += f"- {tip}\n"
        
        text += f"\n*Note: These recommendations are personalized based on your {skin_type} skin type, "
        if weather:
            text += f"{weather.get('temperature', 'N/A')}°C weather, "
        text += f"{occupation} occupation"
        if age:
            text += f", and age {age}"
        text += ".*"
        
        return text
    
    def _personalize_routine(self, base_routine: Dict, weighted_context: Dict, user_info: Dict) -> Dict:
        """Personalize routine based on weighted context"""
        weather = user_info.get("weather", {})
        occupation = user_info.get("occupation", "").lower()
        temp = weather.get("temperature", 20)
        humidity = weather.get("humidity", 50)
        uv_index = weather.get("uv_index", 5)
        
        morning = base_routine["morning"].copy()
        evening = base_routine["evening"].copy()
        
        # Weather modifications
        if temp > 28:  # Hot weather
            # Make products lighter
            morning = [p.replace("Rich", "Lightweight").replace("Heavy", "Light") for p in morning]
            if uv_index >= 7:
                morning = [p.replace("SPF 30+", "SPF 50+") for p in morning]
        elif temp < 10:  # Cold weather
            # Make products richer
            morning = [p.replace("Lightweight", "Rich").replace("Light", "Nourishing") for p in morning]
        
        if humidity < 40:  # Low humidity
            morning.append("Hydrating serum with hyaluronic acid")
        elif humidity > 70:  # High humidity
            morning = [p.replace("Rich", "Gel-based").replace("Cream", "Gel") for p in morning]
        
        # Occupation modifications
        if any(word in occupation for word in ["outdoor", "construction", "field", "driver"]):
            morning.insert(0, "Pre-work deep cleanser")
            morning = [p.replace("SPF 30+", "SPF 50+") for p in morning]
            evening.insert(0, "Post-work double cleanse to remove dirt and pollution")
            evening.append("Antioxidant serum (vitamin C) to combat environmental damage")
        
        if any(word in occupation for word in ["doctor", "nurse", "healthcare", "medical"]):
            morning.append("Barrier repair cream (for mask-wearing)")
            evening.insert(0, "Gentle micellar water (for mask area)")
        
        if any(word in occupation for word in ["engineer", "developer", "programmer", "office", "desk"]):
            morning.append("Blue light protection serum or cream")
            morning.append("Eye cream (for screen time)")
        
        return {"morning": morning, "evening": evening}
    
    def _personalize_products(self, base_products: list, weighted_context: Dict, user_info: Dict) -> list:
        """Personalize products based on weighted context"""
        weather = user_info.get("weather", {})
        occupation = user_info.get("occupation", "").lower()
        temp = weather.get("temperature", 20)
        humidity = weather.get("humidity", 50)
        
        products = base_products.copy()
        
        # Weather-specific additions
        if temp > 28:
            products.append("Mattifying primers (for hot weather)")
            products.append("Cooling gel masks")
        elif temp < 10:
            products.append("Barrier repair creams")
            products.append("Facial oils (for cold weather protection)")
        
        if humidity < 40:
            products.append("Humectant-rich serums")
            products.append("Occlusive night creams")
        elif humidity > 70:
            products.append("Water-based gel products")
            products.append("Non-sticky formulations")
        
        # Occupation-specific additions
        if any(word in occupation for word in ["outdoor", "construction"]):
            products.append("Mineral sunscreens with zinc oxide")
            products.append("Antioxidant serums (vitamin C, E)")
            products.append("Detoxifying masks")
        
        if any(word in occupation for word in ["doctor", "nurse", "healthcare"]):
            products.append("Barrier repair products")
            products.append("Gentle, fragrance-free cleansers")
        
        return products
    
    def _get_lifestyle_tips(self, occupation: str, weather: Dict, age: int = None) -> list:
        """Get lifestyle tips based on occupation, weather, and age"""
        tips = []
        occupation_lower = occupation.lower() if occupation else ""
        
        # Occupation tips
        if any(word in occupation_lower for word in ["outdoor", "construction"]):
            tips.append("Reapply sunscreen every 2 hours during outdoor work")
            tips.append("Wear protective clothing and wide-brimmed hat")
            tips.append("Shower immediately after work to remove pollutants")
        
        if any(word in occupation_lower for word in ["doctor", "nurse", "healthcare"]):
            tips.append("Take mask breaks when possible to let skin breathe")
            tips.append("Use gentle, fragrance-free products to avoid irritation")
            tips.append("Keep a travel-sized moisturizer for frequent hand washing")
        
        if any(word in occupation_lower for word in ["engineer", "developer", "programmer"]):
            tips.append("Take regular breaks from screens to reduce eye strain")
            tips.append("Use blue light blocking products")
            tips.append("Maintain consistent routine despite long work hours")
        
        # Weather tips
        if weather:
            temp = weather.get("temperature", 20)
            humidity = weather.get("humidity", 50)
            uv = weather.get("uv_index", 5)
            
            if temp > 28:
                tips.append("Stay hydrated - drink plenty of water in hot weather")
                tips.append("Use lighter products during day, richer at night")
            elif temp < 10:
                tips.append("Protect skin from wind and cold with richer products")
                tips.append("Consider using a humidifier indoors")
            
            if humidity < 40:
                tips.append("Use humidifier at home/work to combat dry air")
                tips.append("Layer hydrating products")
            elif humidity > 70:
                tips.append("Avoid heavy creams that may feel sticky")
                tips.append("Focus on water-based, quick-absorbing products")
            
            if uv >= 7:
                tips.append("Avoid sun exposure during peak hours (10 AM - 4 PM)")
                tips.append("Wear protective clothing in addition to sunscreen")
        
        # Age tips
        if age:
            if age < 25:
                tips.append("Focus on prevention - establish good habits early")
            elif age > 40:
                tips.append("Consider professional treatments for anti-aging")
                tips.append("Prioritize barrier repair and hydration")
        
        return tips if tips else ["Maintain consistent skincare routine"]
    
    async def _langchain_call(self, weighted_context: Dict[str, Any], user_info: Dict[str, Any]) -> str:
        """LangChain call with structured prompt for personalized recommendations"""
        try:
            # Build comprehensive prompt messages
            messages = self._build_langchain_prompt(weighted_context, user_info)
            
            # Direct async call to LLM
            response = await self.llm.ainvoke(messages)
            result = response.content
            
            # Validate response isn't generic
            if self._is_generic_response(result):
                print("[AI Agent] Response seems generic, retrying with more explicit prompt...")
                # Retry with even more explicit prompt
                result = await self._retry_with_explicit_prompt(weighted_context, user_info)
            
            return result
            
        except Exception as e:
            print(f"[AI Agent] LangChain call error: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to simple direct call
            return await self._simple_llm_call(weighted_context, user_info)
    
    def _build_langchain_prompt(self, weighted_context: Dict[str, Any], user_info: Dict[str, Any]) -> list:
        """Build structured LangChain prompt messages"""
        primary = weighted_context["primary_factors"]
        secondary = weighted_context.get("secondary_factors", {})
        weather = user_info.get("weather", {})
        
        system_message = """You are an expert dermatologist creating UNIQUE, personalized skincare recommendations.

🚨 CRITICAL RULES - READ CAREFULLY:
1. You NEVER give the same product list for the same skin type
2. If someone has OILY SKIN, you MUST give DIFFERENT products based on their weather, occupation, and age
3. The SAME skin type with DIFFERENT factors = COMPLETELY DIFFERENT product recommendations
4. Generic responses like "gentle cleanser, toner, moisturizer, SPF" are FORBIDDEN - you must specify WHY each product is chosen

⚠️ ANTI-PATTERN (WRONG - DO NOT DO THIS):
"Oily skin routine: gentle cleanser, balancing toner, lightweight moisturizer, SPF 30+"
This is WRONG because it ignores weather, occupation, and age.

✅ CORRECT PATTERN:
You must specify products that address the COMBINATION of factors.

EXAMPLES - SAME SKIN TYPE (OILY), DIFFERENT FACTORS = DIFFERENT PRODUCTS:

Example 1: Oily Skin + Hot Weather (35°C) + Construction Worker + Age 25
Morning:
- Pre-work salicylic acid cleanser (combat oil + sweat from heat + physical work)
- Oil-free gel moisturizer with niacinamide (heat makes creams uncomfortable, niacinamide controls oil)
- SPF 50+ zinc oxide sunscreen (outdoor work in high UV)
- Mattifying primer (prevent shine in heat)
Evening:
- Post-work double cleanse with oil cleanser (remove dirt, pollution, sunscreen)
- Clay mask with salicylic acid (2x/week - combat oil from heat + sweat)
- Niacinamide serum (oil control)
- Lightweight gel moisturizer (hydration without heaviness)
Products: Oil-control gel cleansers, mattifying products, SPF 50+, clay masks, niacinamide serums
Reasoning: Hot weather + physical work = maximum oil production, needs aggressive oil control

Example 2: Oily Skin + Cold Weather (5°C) + Office Worker + Age 35
Morning:
- Gentle foaming cleanser (cold weather can dry even oily skin, office AC is drying)
- Hydrating toner with hyaluronic acid (combat office AC dryness)
- Lightweight but hydrating moisturizer with ceramides (balance oil control + prevent dryness from cold/AC)
- SPF 30+ (indoor work, less sun exposure)
- Eye cream with peptides (screen time, age 35 needs eye care)
Evening:
- Oil-based cleanser (gentle, won't over-dry)
- Salicylic acid treatment (2x/week - less frequent than hot weather, cold reduces oil production)
- Hyaluronic acid serum (hydration for dry office environment)
- Barrier-supporting moisturizer (protect from cold + AC)
Products: Gentle cleansers, hydrating toners, ceramide moisturizers, eye creams, barrier repair products
Reasoning: Cold weather + office AC = less oil production but more dryness risk, needs hydration balance

Example 3: Oily Skin + Moderate Weather (20°C) + Healthcare Worker + Age 28
Morning:
- Gentle gel cleanser (won't strip skin, mask-wearing needs gentle care)
- Alcohol-free toner (prevent irritation from masks)
- Lightweight moisturizer with barrier repair (protect from mask friction)
- SPF 30+ (standard protection)
- Barrier cream for mask area (prevent maskne)
Evening:
- Micellar water for mask area (gentle removal)
- Gentle cleanser (frequent washing needs gentle products)
- Salicylic acid spot treatment (for maskne areas only)
- Lightweight gel moisturizer (hydration without heaviness)
Products: Gentle gel cleansers, barrier repair creams, micellar water, spot treatments
Reasoning: Mask-wearing + frequent washing = barrier protection priority, less aggressive oil control needed

NOTICE: All three have OILY SKIN but COMPLETELY DIFFERENT products because:
- Weather changes (hot vs cold vs moderate)
- Occupation changes (construction vs office vs healthcare)
- Age considerations (25 vs 35 vs 28)

YOU MUST DO THE SAME - NEVER REPEAT THE SAME PRODUCTS FOR THE SAME SKIN TYPE."""

        human_message = f"""Create personalized skincare recommendations for this EXACT combination:

SKIN TYPE: {primary['skin_type']['value']} (Base - 40% weight)
Analysis: {primary['skin_type']['analysis']}

WEATHER CONDITIONS (Modify - 30% weight):
- Temperature: {weather.get('temperature', 'N/A')}°C
- Humidity: {weather.get('humidity', 'N/A')}%
- UV Index: {weather.get('uv_index', 'N/A')}
- Condition: {weather.get('condition', 'N/A')}
Weather Analysis: {primary['weather']['analysis']}

OCCUPATION (Modify - 20% weight): {primary['occupation']['value']}
Analysis: {primary['occupation']['analysis']}

AGE (Modify - 10% weight): {secondary.get('age', {}).get('value', 'Not specified') if secondary.get('age') else 'Not specified'}
Analysis: {secondary.get('age', {}).get('analysis', 'N/A') if secondary.get('age') else 'N/A'}

🚨 CRITICAL INSTRUCTIONS:

1. DO NOT give generic "{primary['skin_type']['value']} skin" recommendations
2. DO NOT list the same products you would give to anyone with {primary['skin_type']['value']} skin
3. DO give specific products that address: {primary['skin_type']['value']} skin + {weather.get('temperature', 'N/A')}°C weather + {primary['occupation']['value']} occupation + {secondary.get('age', {}).get('value', 'age') if secondary.get('age') else 'age'} age

4. For EACH product, you MUST explain:
   - Why THIS specific product (not just "cleanser" but "salicylic acid cleanser for oil control in hot weather")
   - How it addresses the COMBINATION of factors
   - What makes it different from generic recommendations

5. VARIATION CHECK: Before submitting, ask:
   - Would someone with {primary['skin_type']['value']} skin but DIFFERENT weather get these same products? If YES, you're wrong - change it.
   - Would someone with {primary['skin_type']['value']} skin but DIFFERENT occupation get these same products? If YES, you're wrong - change it.
   - Would someone with {primary['skin_type']['value']} skin but DIFFERENT age get these same products? If YES, you're wrong - change it.

YOUR TASK:
Create recommendations that are UNIQUE to THIS EXACT combination. 

Provide:
1. **Morning Routine**: 
   - List SPECIFIC products (not generic categories)
   - For EACH product, explain: "I recommend [specific product] because [skin type] + [weather] + [occupation] + [age] = [specific need]"
   - Example: "I recommend salicylic acid gel cleanser because oily skin + hot weather (35°C) + construction work + age 25 = need aggressive oil control to combat heat-induced oil production and sweat"

2. **Evening Routine**: Same level of specificity

3. **Product Recommendations**: 
   - List SPECIFIC product categories with explanations
   - NOT generic like "cleanser, toner, moisturizer"
   - Instead: "Salicylic acid gel cleansers (for oil control in hot weather)", "Mattifying primers (for shine control in heat)"

4. **Lifestyle Tips**: Specific to occupation and weather

5. **Weekly Treatments**: Tailored to this combination

REMEMBER: If your recommendations could apply to ANYONE with {primary['skin_type']['value']} skin, you have FAILED. Make it UNIQUE!"""

        return [
            SystemMessage(content=system_message),
            HumanMessage(content=human_message)
        ]
    
    def _is_generic_response(self, response: str) -> bool:
        """Check if response seems generic - more strict checking"""
        generic_indicators = [
            "gentle cleanser",
            "balancing toner",
            "lightweight moisturizer",
            "SPF 30+ sunscreen",
            "gentle foaming cleanser",
            "alcohol-free toner"
        ]
        
        # Check if response contains generic phrases without specific reasoning
        response_lower = response.lower()
        generic_count = sum(1 for phrase in generic_indicators if phrase in response_lower)
        
        # Check for lack of specific reasoning
        has_specific_reasoning = any(word in response_lower for word in [
            "because", "due to", "since", "as", "for", "combat", "address", "prevent"
        ])
        
        # Check for specific product mentions (not just categories)
        has_specific_products = any(word in response_lower for word in [
            "salicylic acid", "niacinamide", "hyaluronic acid", "ceramide", 
            "zinc oxide", "clay mask", "gel", "mattifying", "barrier repair"
        ])
        
        # Response is generic if:
        # 1. Short AND has multiple generic phrases, OR
        # 2. Has generic phrases but lacks specific reasoning AND specific products
        is_short = len(response) < 800
        has_multiple_generic = generic_count >= 3
        lacks_specificity = not (has_specific_reasoning and has_specific_products)
        
        is_generic = (is_short and has_multiple_generic) or (has_multiple_generic and lacks_specificity)
        
        if is_generic:
            print(f"[AI Agent] Generic response detected: {generic_count} generic phrases, length: {len(response)}, has reasoning: {has_specific_reasoning}, has specific products: {has_specific_products}")
        
        return is_generic
    
    async def _retry_with_explicit_prompt(self, weighted_context: Dict[str, Any], user_info: Dict[str, Any]) -> str:
        """Retry with even more explicit prompt emphasizing variation"""
        primary = weighted_context["primary_factors"]
        secondary = weighted_context.get("secondary_factors", {})
        weather = user_info.get("weather", {})
        age = secondary.get('age', {}).get('value', 'N/A') if secondary.get('age') else 'N/A'
        
        explicit_prompt = f"""🚨 STOP! Your previous response was too generic.

You gave recommendations for {primary['skin_type']['value']} skin, but you gave the SAME products that would work for ANYONE with {primary['skin_type']['value']} skin.

THIS IS WRONG. You must give DIFFERENT products based on:

1. Weather: {weather.get('temperature', 'N/A')}°C, {weather.get('humidity', 'N/A')}% humidity, UV {weather.get('uv_index', 'N/A')}
   - How does THIS specific weather affect {primary['skin_type']['value']} skin?
   - Hot weather? → Need lighter products, more oil control
   - Cold weather? → Need hydration balance, barrier protection
   - High UV? → Need stronger SPF
   - Low humidity? → Need more hydration

2. Occupation: {primary['occupation']['value']}
   - How does THIS occupation affect skincare?
   - Outdoor work? → Need SPF 50+, post-work cleansing, antioxidant protection
   - Office work? → Need blue light protection, eye care, AC-dryness protection
   - Healthcare? → Need barrier repair, mask-friendly products, gentle cleansing

3. Age: {age}
   - How does THIS age affect needs?
   - Younger? → Prevention focus, establish habits
   - Older? → Anti-aging, barrier repair, richer products

DO NOT give:
- "Gentle cleanser" (too generic)
- "Balancing toner" (too generic)
- "Lightweight moisturizer" (too generic)

DO give:
- SPECIFIC products: "Salicylic acid gel cleanser" (explain why for THIS combination)
- SPECIFIC ingredients: "Niacinamide serum" (explain why for THIS combination)
- SPECIFIC formulations: "Oil-free gel moisturizer" (explain why for THIS combination)

For EACH product, explain: "I recommend [specific product] because {primary['skin_type']['value']} skin + {weather.get('temperature', 'N/A')}°C weather + {primary['occupation']['value']} occupation + age {age} = [specific need]"

Create a COMPLETELY UNIQUE routine. If it could apply to anyone with {primary['skin_type']['value']} skin, you're wrong."""
        
        messages = [
            SystemMessage(content="""You are a dermatologist. You create UNIQUE recommendations by combining ALL factors. 
You NEVER give the same products for the same skin type. Each recommendation must be specific to the EXACT combination of skin type + weather + occupation + age.
If you give generic products, you have failed."""),
            HumanMessage(content=explicit_prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        return response.content
    
    async def _simple_llm_call(self, weighted_context: Dict[str, Any], user_info: Dict[str, Any]) -> str:
        """Simple direct LLM call as final fallback"""
        primary = weighted_context["primary_factors"]
        weather = user_info.get("weather", {})
        
        prompt = f"""Create personalized skincare for {primary['skin_type']['value']} skin in {weather.get('temperature', 'N/A')}°C weather, {primary['occupation']['value']} occupation.
Make it specific to this combination, not generic."""
        
        messages = [HumanMessage(content=prompt)]
        response = await self.llm.ainvoke(messages)
        return response.content
    
    def _get_routine_for_skin_type(self, skin_type: str) -> Dict[str, list]:
        routines = {
            "oily": {
                "morning": [
                    "Gentle foaming cleanser",
                    "Alcohol-free toner",
                    "Lightweight, oil-free moisturizer with SPF 30+",
                    "Oil-free sunscreen"
                ],
                "evening": [
                    "Oil-based cleanser (double cleanse)",
                    "Salicylic acid or benzoyl peroxide treatment",
                    "Lightweight gel moisturizer",
                    "Retinol serum (2-3 times per week)"
                ]
            },
            "dry": {
                "morning": [
                    "Cream or oil-based cleanser",
                    "Hydrating toner",
                    "Rich moisturizer with ceramides",
                    "SPF 30+ sunscreen"
                ],
                "evening": [
                    "Gentle cream cleanser",
                    "Hydrating serum with hyaluronic acid",
                    "Rich night cream",
                    "Face oil (optional)"
                ]
            },
            "normal": {
                "morning": [
                    "Gentle cleanser",
                    "Balancing toner",
                    "Lightweight moisturizer",
                    "SPF 30+ sunscreen"
                ],
                "evening": [
                    "Gentle cleanser",
                    "Antioxidant serum",
                    "Moisturizer",
                    "Weekly exfoliation"
                ]
            }
        }
        return routines.get(skin_type, routines["normal"])
    
    def _get_products_for_skin_type(self, skin_type: str) -> list:
        products = {
            "oily": [
                "Oil-free cleansers",
                "Salicylic acid products",
                "Clay masks",
                "Non-comedogenic moisturizers",
                "Mattifying primers"
            ],
            "dry": [
                "Cream cleansers",
                "Hyaluronic acid serums",
                "Ceramide moisturizers",
                "Face oils",
                "Gentle exfoliants"
            ],
            "normal": [
                "Balanced cleansers",
                "Antioxidant serums",
                "Lightweight moisturizers",
                "Regular exfoliants",
                "SPF protection"
            ]
        }
        return products.get(skin_type, products["normal"])
    
    def _get_weather_tips(self, weather: Dict) -> list:
        tips = []
        if weather:
            temp = weather.get("temperature", 20)
            humidity = weather.get("humidity", 50)
            uv = weather.get("uv_index", 5)
            
            if uv > 6:
                tips.append("High UV index - use SPF 50+ and reapply every 2 hours")
            if humidity < 40:
                tips.append("Low humidity - increase moisturizer usage")
            if temp > 25:
                tips.append("Hot weather - use lighter products and stay hydrated")
            if temp < 10:
                tips.append("Cold weather - use richer moisturizers to protect skin barrier")
        
        return tips if tips else ["Maintain consistent skincare routine"]

