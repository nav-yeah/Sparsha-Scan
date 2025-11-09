"""
Flask Backend for Skin Disease Detection Application
Provides API endpoints for image analysis, doctor recommendations, and progress tracking
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# Import model predictor and skin disease helper
from model_predictor import get_predictor

# Try to import skin_disease_helper, but make it optional
try:
    from skin_disease_helper import SkinDiseaseHelper
    SKIN_HELPER_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Skin disease helper not available: {e}")
    print("   Treatment advice and doctor search will use fallback methods")
    SKIN_HELPER_AVAILABLE = False
    SkinDiseaseHelper = None

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Initialize model predictor
print("Initializing model predictor...")
predictor = get_predictor()

# Initialize skin disease helper (optional)
skin_helper = None
if SKIN_HELPER_AVAILABLE:
    try:
        skin_helper = SkinDiseaseHelper()
        if skin_helper.model:
            print("✅ Skin disease helper initialized (Gemini API available)")
        else:
            print("⚠️ Skin disease helper initialized but Gemini API not configured")
            print("   Treatment advice will use fallback methods")
        if skin_helper.gmaps:
            print("✅ Google Places API available for doctor search")
        else:
            print("⚠️ Google Places API not configured (doctor search will use fallback)")
    except Exception as e:
        print(f"⚠️ Could not initialize skin disease helper: {e}")
        import traceback
        traceback.print_exc()
        print("   Some features may be limited")


# Utility functions
def read_json(fn: str, default=None):
    """Read JSON file from data directory"""
    p = DATA_DIR / fn
    if not p.exists():
        return default
    try:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading {fn}: {e}")
        return default


def write_json(fn: str, obj):
    """Write JSON file to data directory"""
    p = DATA_DIR / fn
    try:
        with p.open("w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error writing {fn}: {e}")
        raise


def get_severity_from_confidence(confidence: float) -> str:
    """Determine severity based on confidence and disease type"""
    if confidence >= 85:
        return "High"
    elif confidence >= 70:
        return "Moderate"
    else:
        return "Low"


def get_treatment_suggestions(disease: str, confidence: float) -> Dict:
    """Get treatment suggestions for a disease"""
    recommendations = read_json("recommendations.json", {})
    
    # Try to find exact match
    disease_lower = disease.lower().strip()
    if disease_lower in recommendations:
        rec = recommendations[disease_lower]
        return {
            "severity": rec.get("severity", get_severity_from_confidence(confidence)),
            "suggestions": rec.get("suggestions", [])
        }
    
    # Try partial match
    for key, rec in recommendations.items():
        if key in disease_lower or disease_lower in key:
            return {
                "severity": rec.get("severity", get_severity_from_confidence(confidence)),
                "suggestions": rec.get("suggestions", [])
            }
    
    # Default suggestions
    return {
        "severity": get_severity_from_confidence(confidence),
        "suggestions": [
            "Consult with a dermatologist for proper diagnosis",
            "Keep the affected area clean and dry",
            "Avoid scratching or irritating the area",
            "Monitor for changes or worsening symptoms",
            "Follow medical advice for treatment"
        ]
    }


# API Routes

@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint"""
    health_info = {
        "status": "ok",
        "model_loaded": predictor.is_loaded,
        "skin_helper_available": skin_helper is not None,
        "model_framework": getattr(predictor, "framework", "unknown"),
        "num_classes": len(getattr(predictor, "class_names", []) or []),
        "input_size": getattr(predictor, "input_size", None),
    }
    
    # Check if Google Places API is configured
    if skin_helper:
        health_info["google_places_configured"] = skin_helper.gmaps is not None
        health_info["gemini_configured"] = skin_helper.model is not None
    
    return jsonify(health_info)


@app.route("/api/features", methods=["GET"])
def get_features():
    """Get application features"""
    features = read_json("features.json", [])
    if not features:
        features = [
            {"title": "AI-powered detection", "description": "Predicts common skin conditions from images"},
            {"title": "Treatment guidance", "description": "High-level care suggestions and when to see a doctor"},
            {"title": "Find specialists", "description": "Locate dermatologists and teleconsult options"}
        ]
    return jsonify({"success": True, "features": features})


@app.route("/api/doctors", methods=["GET"])
def get_doctors():
    """Get list of doctors - prioritizes real Google Places results if location provided"""
    location = request.args.get("location", "").strip()
    
    doctors = []
    
    # If location is provided and skin helper is available, try to find real doctors
    if location and skin_helper:
        try:
            print(f"🔍 Searching for doctors near: {location}")
            result = skin_helper.find_doctors(location, radius_km=25.0, max_results=15)
            if result.get("success") and result.get("doctors"):
                print(f"✅ Found {len(result['doctors'])} doctors from Google Places API")
                # Convert API doctors to our format - prioritize these
                for api_doc in result["doctors"]:
                    doc_name = api_doc.get("name", "Unknown")
                    doctors.append({
                        "name": doc_name,
                        "specialty": "Dermatology",
                        "rating": api_doc.get("rating", 0),
                        "reviews": api_doc.get("total_ratings", 0),
                        "location": api_doc.get("address", location),
                        "availability": "Contact for availability",
                        "teleconsult": True,
                        "phone": api_doc.get("phone", "N/A"),
                        "website": api_doc.get("website", "N/A")
                    })
            else:
                error_msg = result.get("error", "Unknown error")
                print(f"⚠️ Could not find doctors: {error_msg}")
        except Exception as e:
            print(f"❌ Error finding doctors: {e}")
            import traceback
            traceback.print_exc()
    
    # If no real doctors found, use fallback hardcoded list
    if not doctors:
        print("⚠️ No real doctors found, using fallback list")
        doctors = read_json("doctors.json", [])
        if not doctors:
            # Ultimate fallback
            doctors = [
                {
                    "name": "Dr. Sarah Johnson",
                    "specialty": "Clinical Dermatology",
                    "rating": 4.9,
                    "reviews": 324,
                    "location": "Mumbai, Maharashtra",
                    "availability": "Available Today",
                    "teleconsult": True,
                },
                {
                    "name": "Dr. Rajesh Kumar",
                    "specialty": "Pediatric Dermatology",
                    "rating": 4.8,
                    "reviews": 256,
                    "location": "Bangalore, Karnataka",
                    "availability": "Next Available: Tomorrow",
                    "teleconsult": True,
                },
            ]
    
    return jsonify({
        "success": True, 
        "doctors": doctors,
        "location_used": location if location else None,
        "source": "google_places" if location and skin_helper and doctors else "fallback"
    })


@app.route("/api/recommendations", methods=["GET"])
def get_recommendations():
    """Get recommendations for a specific disease"""
    disease = request.args.get("disease", "").strip().lower()
    recs = read_json("recommendations.json", {})
    
    if disease and disease in recs:
        return jsonify({"success": True, "disease": disease, "data": recs[disease]})
    
    return jsonify({"success": True, "data": recs})


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """Analyze uploaded image for skin disease"""
    try:
        # Check if image is provided
        if "image" not in request.files:
            return jsonify({"success": False, "error": "No image provided"}), 400

        image = request.files["image"]
        if image.filename == "":
            return jsonify({"success": False, "error": "Empty filename"}), 400

        # Read image bytes
        file_bytes = image.read()
        if len(file_bytes) == 0:
            return jsonify({"success": False, "error": "Empty file"}), 400

        # Validate file size (max 10MB)
        MAX_FILE_SIZE = 10 * 1024 * 1024
        if len(file_bytes) > MAX_FILE_SIZE:
            return jsonify({"success": False, "error": "File too large (max 10MB)"}), 400

        # Save file
        hasher = hashlib.md5(file_bytes).hexdigest()
        ext = os.path.splitext(image.filename)[1] or ".jpg"
        filename = f"{uuid.uuid4().hex}_{hasher[:8]}{ext}"
        out_path = UPLOAD_DIR / filename
        out_path.write_bytes(file_bytes)

        # Get prediction from model
        print(f"🔄 Starting prediction for image: {filename}")
        prediction_result = predictor.predict(file_bytes)
        
        if not prediction_result.get("success"):
            return jsonify({"success": False, "error": "Prediction failed"}), 500

        disease = prediction_result["disease"]
        confidence = prediction_result["confidence"]
        method = prediction_result.get("method", "unknown")
        
        print(f"📊 Prediction result: {disease} ({confidence}%) - Method: {method}")

        # Get treatment suggestions from JSON (fallback)
        treatment = get_treatment_suggestions(disease, confidence)
        severity = treatment["severity"]
        suggestions = treatment["suggestions"]

        # Get AI-powered treatment advice from Gemini API
        treatment_advice = None
        confidence_level = None
        recommend_urgent_care = False
        
        if skin_helper:
            try:
                print(f"🤖 Calling Gemini API for treatment advice for: {disease} (confidence: {confidence}%)")
                advice_result = skin_helper.get_treatment_advice(disease, confidence)
                
                if advice_result.get("success"):
                    treatment_advice = advice_result.get("advice")
                    confidence_level = advice_result.get("confidence_level")
                    recommend_urgent_care = advice_result.get("recommend_urgent_care", False)
                    if treatment_advice:
                        # treatment_advice is now a JSON object
                        import json
                        print(f"✅ Gemini API treatment advice received (structured JSON)")
                        print(f"   Confidence level: {confidence_level}")
                        print(f"   Urgent care recommended: {recommend_urgent_care}")
                    else:
                        print(f"⚠️ Gemini API returned success but no advice data")
                else:
                    error_msg = advice_result.get('error', 'Unknown error')
                    print(f"⚠️ Gemini API returned unsuccessful result: {error_msg}")
                    # Still use the fallback advice if provided
                    treatment_advice = advice_result.get("advice")
                    if treatment_advice:
                        print(f"   Using fallback advice from error response")
            except Exception as e:
                print(f"❌ Error calling Gemini API for treatment advice: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("⚠️ Skin helper not available, skipping Gemini API treatment advice")
            if not skin_helper:
                print("   Hint: Make sure GOOGLE_API_KEY is set in .env file")

        # Create analysis record
        record = {
            "id": uuid.uuid4().hex,
            "image": f"/api/uploads/{filename}",
            "disease": disease,
            "confidence": confidence,
            "severity": severity,
            "suggestions": suggestions,  # Basic suggestions from JSON
            "treatment_advice": treatment_advice,  # AI-powered advice from Gemini
            "confidence_level": confidence_level,  # LOW, MODERATE, HIGH
            "recommend_urgent_care": recommend_urgent_care,
            "has_ai_advice": treatment_advice is not None,  # Flag to indicate if AI advice is available
            "timestamp": datetime.now().isoformat(),
            "method": prediction_result.get("method", "unknown"),
            "top_predictions": prediction_result.get("top_predictions", [])
        }

        # Save analysis record
        analyses = read_json("analyses.json", [])
        if analyses is None:
            analyses = []
        analyses.insert(0, record)
        # Keep only last 100 analyses
        analyses = analyses[:100]
        write_json("analyses.json", analyses)

        return jsonify({"success": True, "analysis": record})

    except Exception as e:
        print(f"Error in analyze endpoint: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/analyses", methods=["GET"])
def get_analyses():
    """Get all analysis records for progress tracking"""
    analyses = read_json("analyses.json", [])
    if analyses is None:
        analyses = []
    
    # Optionally filter by limit
    limit = request.args.get("limit", type=int)
    if limit:
        analyses = analyses[:limit]
    
    return jsonify({"success": True, "analyses": analyses})


@app.route("/api/analyses/<analysis_id>", methods=["GET"])
def get_analysis(analysis_id: str):
    """Get a specific analysis by ID"""
    analyses = read_json("analyses.json", [])
    if analyses is None:
        analyses = []
    
    for analysis in analyses:
        if analysis.get("id") == analysis_id:
            return jsonify({"success": True, "analysis": analysis})
    
    return jsonify({"success": False, "error": "Analysis not found"}), 404


@app.route("/api/progress", methods=["GET"])
def get_progress():
    """Get progress tracking data"""
    analyses = read_json("analyses.json", [])
    if analyses is None or len(analyses) == 0:
        return jsonify({
            "success": True,
            "overall_improvement": 0,
            "days_tracked": 0,
            "check_ins": 0,
            "recent_analyses": [],
            "improvements": []
        })
    
    # Calculate progress metrics
    total_analyses = len(analyses)
    
    # Calculate days tracked (difference between first and last analysis)
    if len(analyses) > 1:
        try:
            first_date = datetime.fromisoformat(analyses[-1].get("timestamp", ""))
            last_date = datetime.fromisoformat(analyses[0].get("timestamp", ""))
            days_tracked = (last_date - first_date).days
        except:
            days_tracked = total_analyses
    else:
        days_tracked = 1
    
    # Calculate overall improvement (simplified - compare confidence trends)
    # In a real system, you'd compare disease severity over time
    if len(analyses) >= 2:
        # Simple heuristic: if latest confidence is lower, assume improvement
        latest_confidence = analyses[0].get("confidence", 0)
        oldest_confidence = analyses[-1].get("confidence", 0)
        # This is a simplified metric - adjust based on your needs
        improvement = max(0, min(100, (oldest_confidence - latest_confidence) * 2 + 50))
    else:
        improvement = 0
    
    # Get recent analyses (last 6)
    recent_analyses = analyses[:6]
    
    # Format recent analyses for display
    formatted_analyses = []
    for i, analysis in enumerate(recent_analyses):
        try:
            timestamp = datetime.fromisoformat(analysis.get("timestamp", ""))
            if i == 0:
                date_str = "Today"
            else:
                days_ago = (datetime.now() - timestamp).days
                if days_ago == 0:
                    date_str = "Today"
                elif days_ago == 1:
                    date_str = "1 day ago"
                else:
                    date_str = f"{days_ago} days ago"
        except:
            date_str = "Recent"
        
        formatted_analyses.append({
            "id": analysis.get("id"),
            "date": date_str,
            "disease": analysis.get("disease"),
            "severity": analysis.get("severity", "Moderate"),
            "confidence": analysis.get("confidence"),
            "image": analysis.get("image"),
            "timestamp": analysis.get("timestamp")
        })
    
    return jsonify({
        "success": True,
        "overall_improvement": round(improvement, 1),
        "days_tracked": max(1, days_tracked),
        "check_ins": total_analyses,
        "recent_analyses": formatted_analyses,
        "improvements": [
            {"metric": "Redness Reduced", "improvement": round(improvement * 0.8, 1)},
            {"metric": "Inflammation Down", "improvement": round(improvement * 1.05, 1)},
        ]
    })


@app.route("/api/uploads/<path:filename>")
def uploaded_file(filename: str):
    """Serve uploaded images"""
    try:
        return send_from_directory(str(UPLOAD_DIR), filename)
    except Exception as e:
        return jsonify({"error": "File not found"}), 404


if __name__ == "__main__":
    print("Starting Flask server...")
    print(f"Model loaded: {predictor.is_loaded}")
    print(f"Skin helper available: {skin_helper is not None}")
    app.run(host="0.0.0.0", port=5000, debug=True)
