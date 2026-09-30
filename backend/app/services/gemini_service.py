import os
import json
import logging
from typing import Dict, Any, Optional
from PIL import Image
from dotenv import load_dotenv

from app.utils.prompts import (
    build_home_prompt,
    build_party_prompt,
    build_jewelry_prompt,
    build_search_url,
)
from app.services.budget_service import allocate_home_budget, allocate_party_budget, enforce_budget_limit

load_dotenv()

logger = logging.getLogger("pocketsmart.gemini")

# Model preferences in order
GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]


def get_gemini_client():
    """Returns a Google GenAI Client if a valid API key is present."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key in ("your_api_key_here", "your_gemini_api_key_here", "None"):
        return None
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except Exception as e:
        logger.warning(f"Failed to initialize Google GenAI Client: {e}")
        return None


def clean_and_parse_json(text: str) -> Optional[Dict[str, Any]]:
    """Clean markdown json formatting and safely parse JSON."""
    if not text:
        return None
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}. Raw content: {cleaned[:300]}")
        return None


# ---------------------------------------------------------------------------
# Fallback / Demo Recommendations
# ---------------------------------------------------------------------------

def get_home_fallback(data: Dict[str, Any]) -> Dict[str, Any]:
    """Smart algorithmic fallback for Home Interior recommendations when Gemini is unavailable."""
    budget = float(data.get("budget", 50000))
    currency = data.get("currency", "₹")
    room_type = data.get("room_type", "Living Room")
    style = data.get("style", "Modern")

    allocations = allocate_home_budget(budget, room_type=room_type, style=style)
    
    # Generate realistic items scaled to the budget
    furn_alloc = next((a["allocated_amount"] for a in allocations if a["category"] == "Furniture"), budget * 0.45)
    light_alloc = next((a["allocated_amount"] for a in allocations if a["category"] == "Lighting"), budget * 0.15)
    decor_alloc = next((a["allocated_amount"] for a in allocations if a["category"] == "Decor"), budget * 0.15)
    storage_alloc = next((a["allocated_amount"] for a in allocations if a["category"] == "Storage"), budget * 0.12)

    raw_items = [
        {
            "product_name": f"{style} Modular Seating Sofa",
            "category": "Furniture",
            "estimated_price": round(furn_alloc * 0.65, 2),
            "reason": f"Sleek and comfortable design tailored for {room_type}, fitting neatly into the furniture budget.",
            "style": style,
            "color_or_material": "Neutral Fabric / Wood",
            "platform": "Amazon",
            "search_query": f"{style} sofa for {room_type}"
        },
        {
            "product_name": f"Minimalist Accent Coffee & Side Table Set",
            "category": "Furniture",
            "estimated_price": round(furn_alloc * 0.28, 2),
            "reason": f"Functional centerpiece matching {style} decor with durable finish.",
            "style": style,
            "color_or_material": "Engineered Wood & Metal",
            "platform": "Pepperfry",
            "search_query": f"{style} coffee table set"
        },
        {
            "product_name": "Warm LED Pendant Ceiling & Floor Lamp Set",
            "category": "Lighting",
            "estimated_price": round(light_alloc * 0.85, 2),
            "reason": "Provides cozy, layered ambient illumination without high power consumption.",
            "style": style,
            "color_or_material": "Warm White / Matte Black",
            "platform": "Amazon",
            "search_query": f"{style} modern pendant floor lamp"
        },
        {
            "product_name": f"Textured Geometric Area Rug & Matching Cushions",
            "category": "Decor",
            "estimated_price": round(decor_alloc * 0.80, 2),
            "reason": f"Adds warmth, acoustics, and cohesive color balance to your {room_type}.",
            "style": style,
            "color_or_material": "Soft Microfiber & Cotton",
            "platform": "Flipkart",
            "search_query": f"{style} area rug and cushions set"
        },
        {
            "product_name": "Wall-Mounted Floating Display Shelves",
            "category": "Storage",
            "estimated_price": round(storage_alloc * 0.80, 2),
            "reason": "Maximizes vertical storage space while keeping floor area clutter-free.",
            "style": style,
            "color_or_material": "Walnut finish wood",
            "platform": "Urban Ladder",
            "search_query": f"floating wall storage shelves"
        }
    ]

    # Attach legitimate search links
    for item in raw_items:
        item["search_url"] = build_search_url(item["platform"], item.get("search_query", item["product_name"]))

    valid_recs, total_est, reserve = enforce_budget_limit(raw_items, budget)

    return {
        "planner_type": "home",
        "total_budget": budget,
        "currency": currency,
        "total_estimated": total_est,
        "remaining_reserve": reserve,
        "allocations": allocations,
        "recommendations": valid_recs,
        "is_fallback": True,
        "ai_notes": "⚡ DEMO FALLBACK MODE: Generated using intelligent local budget heuristics. To unlock real-time Gemini AI reasoning, set a valid GEMINI_API_KEY in backend/.env."
    }


def get_party_fallback(data: Dict[str, Any]) -> Dict[str, Any]:
    """Smart algorithmic fallback for Party Planner when Gemini is unavailable."""
    budget = float(data.get("budget", 30000))
    currency = data.get("currency", "₹")
    event_type = data.get("event_type", "Birthday")
    guest_count = max(1, int(data.get("guest_count", 25)))
    location = data.get("location", "City")
    venue_req = data.get("venue_requirement", "Needed")
    food_pref = data.get("food_preference", "Both")
    decor_level = data.get("decoration_level", "Standard")

    allocations = allocate_party_budget(
        budget,
        guest_count=guest_count,
        venue_req=venue_req,
        food_pref=food_pref,
        decor_level=decor_level
    )

    food_alloc = next((a["allocated_amount"] for a in allocations if a["category"] == "Food & Catering"), budget * 0.40)
    venue_alloc = next((a["allocated_amount"] for a in allocations if a["category"] == "Venue & Space"), budget * 0.25)
    decor_alloc = next((a["allocated_amount"] for a in allocations if a["category"] == "Decoration"), budget * 0.15)
    ent_alloc = next((a["allocated_amount"] for a in allocations if a["category"] == "Entertainment & Music"), budget * 0.10)

    cost_per_guest = round(food_alloc / guest_count, 2)

    raw_items = [
        {
            "product_name": f"{event_type} Party Buffet Catering ({food_pref})",
            "category": "Food & Catering",
            "estimated_price": round(food_alloc * 0.90, 2),
            "reason": f"Complete multi-course meal package serving ~{guest_count} guests at ~{currency}{cost_per_guest:,.0f}/person.",
            "style": f"{food_pref} Gourmet Spread",
            "color_or_material": "Hot Buffet Service",
            "platform": "Zomato",
            "search_query": f"catering for {event_type} in {location}"
        },
        {
            "product_name": f"{decor_level} Balloon Arch & Themed Backdrop Kit",
            "category": "Decoration",
            "estimated_price": round(decor_alloc * 0.85, 2),
            "reason": f"Eye-catching {decor_level.lower()} photo corner with banners, fairy lights, and metallic balloons.",
            "style": f"{decor_level} Event Theme",
            "color_or_material": "Pastel & Metallic Foil",
            "platform": "Amazon",
            "search_query": f"{event_type} decoration party kit with backdrop"
        },
        {
            "product_name": "Portable High-Power Bluetooth Party Speaker with Mic",
            "category": "Entertainment & Music",
            "estimated_price": round(ent_alloc * 0.85, 2),
            "reason": "Allows high-clarity background music, announcements, and karaoke without hiring an expensive DJ.",
            "style": "Wireless Audio",
            "color_or_material": "Heavy Bass with LED Lights",
            "platform": "Amazon",
            "search_query": "party bluetooth speaker with wireless mic"
        },
        {
            "product_name": "Venue Hall & Seating Arrangement",
            "category": "Venue & Space",
            "estimated_price": round(venue_alloc * 0.85, 2),
            "reason": f"Community hall or private banquet room comfortably accommodating {guest_count} attendees.",
            "style": "Banquet / Private Room",
            "color_or_material": "Air-conditioned with tables & chairs",
            "platform": "OYO",
            "search_query": f"party hall or banquet room in {location}"
        }
    ]

    for item in raw_items:
        item["search_url"] = build_search_url(item["platform"], item.get("search_query", item["product_name"]))

    valid_recs, total_est, reserve = enforce_budget_limit(raw_items, budget)

    return {
        "planner_type": "party",
        "total_budget": budget,
        "currency": currency,
        "event_type": event_type,
        "guest_count": guest_count,
        "cost_per_guest": cost_per_guest,
        "total_estimated": total_est,
        "remaining_reserve": reserve,
        "allocations": allocations,
        "recommendations": valid_recs,
        "is_fallback": True,
        "ai_notes": "⚡ DEMO FALLBACK MODE: Generated using dynamic algorithmic distribution. To activate live Gemini event optimization, configure GEMINI_API_KEY in backend/.env."
    }


def get_jewelry_fallback(data: Dict[str, Any], has_image: bool = False) -> Dict[str, Any]:
    """Smart algorithmic fallback for Jewelry recommendations when Gemini is unavailable."""
    budget = float(data.get("budget", 15000))
    currency = data.get("currency", "₹")
    occasion = data.get("occasion", "Wedding")
    style = data.get("style", "Traditional")
    jewelry_type = data.get("jewelry_type", "Full Set")
    material = data.get("preferred_color_material", "Gold / Kundan") or "Gold / Kundan"
    outfit_desc = data.get("outfit_description", "") or "Classic festive attire"

    outfit_analysis = {
        "dominant_colors": ["Maroon", "Gold", "Cream"],
        "outfit_style": outfit_desc if outfit_desc else f"Classic {occasion} Ensemble",
        "formality": "High Traditional Festive" if occasion in ["Wedding", "Festival", "Engagement"] else "Semi-Formal",
        "suitable_jewelry_style": f"{style} Fine Jewelry",
        "suitable_metal_or_gems": material,
        "styling_advice": "Focus on a statement centerpiece (like a choker or jhumkas) while balancing complementary smaller accessories."
    }

    raw_items = [
        {
            "product_name": f"{style} {material} Choker / Statement Necklace",
            "category": "Necklace",
            "estimated_price": round(budget * 0.50, 2),
            "reason": f"Serves as the eye-catching focal point, perfectly suited for {occasion}.",
            "style": style,
            "color_or_material": material,
            "platform": "Tanishq",
            "search_query": f"{style} {material} necklace {occasion}"
        },
        {
            "product_name": f"Matching {style} Chandbali / Jhumka Earrings",
            "category": "Earrings",
            "estimated_price": round(budget * 0.25, 2),
            "reason": "Frames the face elegantly without clashing with the necklace collar.",
            "style": style,
            "color_or_material": material,
            "platform": "CaratLane",
            "search_query": f"{style} earrings {material}"
        },
        {
            "product_name": f"Handcrafted {style} Bangles / Kada Pair",
            "category": "Bangles",
            "estimated_price": round(budget * 0.18, 2),
            "reason": "Adds delicate wrist charm that balances the overall attire aesthetic.",
            "style": style,
            "color_or_material": material,
            "platform": "Myntra",
            "search_query": f"{style} bangles {material}"
        }
    ]

    for item in raw_items:
        item["search_url"] = build_search_url(item["platform"], item.get("search_query", item["product_name"]))

    valid_recs, total_est, reserve = enforce_budget_limit(raw_items, budget)

    return {
        "planner_type": "jewelry",
        "total_budget": budget,
        "currency": currency,
        "occasion": occasion,
        "total_estimated": total_est,
        "remaining_reserve": reserve,
        "outfit_analysis": outfit_analysis,
        "recommendations": valid_recs,
        "is_fallback": True,
        "ai_notes": "⚡ DEMO FALLBACK MODE: Generated using expert fashion styling rules. To activate image-recognition & Gemini Flash generative styling, configure GEMINI_API_KEY in backend/.env."
    }


# ---------------------------------------------------------------------------
# Gemini Generation Functions
# ---------------------------------------------------------------------------

def generate_home_recommendations(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate home interior budget recommendations via Gemini with automatic fallback."""
    client = get_gemini_client()
    if not client:
        return get_home_fallback(data)

    prompt = build_home_prompt(data)
    response_json = None

    for model_name in GEMINI_MODELS:
        try:
            logger.info(f"Invoking Gemini model: {model_name} for Home Planner...")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            response_json = clean_and_parse_json(response.text)
            if response_json:
                break
        except Exception as e:
            logger.warning(f"Error calling {model_name}: {e}")

    if not response_json:
        return get_home_fallback(data)

    try:
        budget = float(data.get("budget", 50000))
        currency = data.get("currency", "₹")
        allocations = response_json.get("allocations", [])
        raw_recs = response_json.get("recommendations", [])

        # Enrich search URLs
        for item in raw_recs:
            platform = item.get("platform", "Amazon")
            query = item.get("search_query", item.get("product_name", "Home Interior Item"))
            item["search_url"] = build_search_url(platform, query)

        valid_recs, total_est, reserve = enforce_budget_limit(raw_recs, budget)

        return {
            "planner_type": "home",
            "total_budget": budget,
            "currency": currency,
            "total_estimated": total_est,
            "remaining_reserve": reserve,
            "allocations": allocations if allocations else allocate_home_budget(budget),
            "recommendations": valid_recs,
            "is_fallback": False,
            "ai_notes": response_json.get("ai_notes", "Powered by Google Gemini Flash")
        }
    except Exception as e:
        logger.error(f"Error structuring Gemini response: {e}")
        return get_home_fallback(data)


def generate_party_recommendations(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate party planning and dynamic budget allocation via Gemini with automatic fallback."""
    client = get_gemini_client()
    if not client:
        return get_party_fallback(data)

    prompt = build_party_prompt(data)
    response_json = None

    for model_name in GEMINI_MODELS:
        try:
            logger.info(f"Invoking Gemini model: {model_name} for Party Planner...")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            response_json = clean_and_parse_json(response.text)
            if response_json:
                break
        except Exception as e:
            logger.warning(f"Error calling {model_name}: {e}")

    if not response_json:
        return get_party_fallback(data)

    try:
        budget = float(data.get("budget", 30000))
        currency = data.get("currency", "₹")
        guest_count = int(data.get("guest_count", 20))
        cost_per_guest = float(response_json.get("cost_per_guest", round(budget / max(1, guest_count), 2)))
        allocations = response_json.get("allocations", [])
        raw_recs = response_json.get("recommendations", [])

        for item in raw_recs:
            platform = item.get("platform", "Amazon")
            query = item.get("search_query", item.get("product_name", "Party supplies"))
            item["search_url"] = build_search_url(platform, query)

        valid_recs, total_est, reserve = enforce_budget_limit(raw_recs, budget)

        return {
            "planner_type": "party",
            "total_budget": budget,
            "currency": currency,
            "event_type": data.get("event_type", "Event"),
            "guest_count": guest_count,
            "cost_per_guest": cost_per_guest,
            "total_estimated": total_est,
            "remaining_reserve": reserve,
            "allocations": allocations if allocations else allocate_party_budget(budget, guest_count),
            "recommendations": valid_recs,
            "is_fallback": False,
            "ai_notes": response_json.get("ai_notes", "Personalized event plan generated with Google Gemini Flash")
        }
    except Exception as e:
        logger.error(f"Error processing Gemini party response: {e}")
        return get_party_fallback(data)


def generate_jewelry_recommendations(data: Dict[str, Any], image_path: Optional[str] = None) -> Dict[str, Any]:
    """Generate jewelry budget recommendations, with optional image vision analysis via Gemini."""
    client = get_gemini_client()
    has_image = bool(image_path and os.path.exists(image_path))

    if not client:
        return get_jewelry_fallback(data, has_image=has_image)

    prompt = build_jewelry_prompt(data, has_image=has_image)
    contents = []

    if has_image:
        try:
            img = Image.open(image_path)
            contents.append(img)
        except Exception as e:
            logger.warning(f"Could not load image at {image_path}: {e}")

    contents.append(prompt)
    response_json = None

    for model_name in GEMINI_MODELS:
        try:
            logger.info(f"Invoking Gemini model: {model_name} for Jewelry Planner (Image: {has_image})...")
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
            )
            response_json = clean_and_parse_json(response.text)
            if response_json:
                break
        except Exception as e:
            logger.warning(f"Error calling {model_name}: {e}")

    if not response_json:
        return get_jewelry_fallback(data, has_image=has_image)

    try:
        budget = float(data.get("budget", 15000))
        currency = data.get("currency", "₹")
        outfit_analysis = response_json.get("outfit_analysis")
        raw_recs = response_json.get("recommendations", [])

        for item in raw_recs:
            platform = item.get("platform", "Tanishq")
            query = item.get("search_query", item.get("product_name", "Jewelry piece"))
            item["search_url"] = build_search_url(platform, query)

        valid_recs, total_est, reserve = enforce_budget_limit(raw_recs, budget)

        return {
            "planner_type": "jewelry",
            "total_budget": budget,
            "currency": currency,
            "occasion": data.get("occasion", "Occasion"),
            "total_estimated": total_est,
            "remaining_reserve": reserve,
            "outfit_analysis": outfit_analysis,
            "recommendations": valid_recs,
            "is_fallback": False,
            "ai_notes": response_json.get("ai_notes", "Curated jewelry styling by Google Gemini Flash")
        }
    except Exception as e:
        logger.error(f"Error parsing Gemini jewelry response: {e}")
        return get_jewelry_fallback(data, has_image=has_image)
