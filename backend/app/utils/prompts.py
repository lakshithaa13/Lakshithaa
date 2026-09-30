import urllib.parse


def build_search_url(platform: str, query: str) -> str:
    """
    Generate legitimate e-commerce / service search URLs without inventing fake product IDs.
    """
    encoded_query = urllib.parse.quote_plus(query.strip())
    platform_lower = platform.lower()

    if "amazon" in platform_lower:
        return f"https://www.amazon.in/s?k={encoded_query}"
    elif "flipkart" in platform_lower:
        return f"https://www.flipkart.com/search?q={encoded_query}"
    elif "pepperfry" in platform_lower:
        return f"https://www.pepperfry.com/site_product/search?q={encoded_query}"
    elif "urban ladder" in platform_lower:
        return f"https://www.urbanladder.com/products/search?keywords={encoded_query}"
    elif "myntra" in platform_lower:
        return f"https://www.myntra.com/{encoded_query}"
    elif "ajio" in platform_lower:
        return f"https://www.ajio.com/search/?text={encoded_query}"
    elif "tanishq" in platform_lower:
        return f"https://www.tanishq.co.in/shop?q={encoded_query}"
    elif "caratlane" in platform_lower:
        return f"https://www.caratlane.com/search?q={encoded_query}"
    elif "zomato" in platform_lower:
        return f"https://www.zomato.com/search?q={encoded_query}"
    elif "swiggy" in platform_lower:
        return f"https://www.swiggy.com/search?query={encoded_query}"
    elif "oyo" in platform_lower:
        return f"https://www.oyorooms.com/search?q={encoded_query}"
    elif "ikea" in platform_lower:
        return f"https://www.ikea.com/in/en/search/?q={encoded_query}"
    else:
        # Default to Google Shopping / Search
        return f"https://www.google.com/search?q={encoded_query}&tbm=shop"


def build_home_prompt(data: dict) -> str:
    """Prompt for Gemini to generate home interior budget allocation and product recommendations."""
    return f"""
You are an expert interior designer and budget consultant for PocketSmart AI.
Analyze the following home interior requirements and budget carefully.

User Requirements:
- Total Budget: {data.get('currency', '₹')}{data.get('budget')}
- Room Type: {data.get('room_type')}
- Design Style: {data.get('style')}
- Quantities Requested:
  * Sofas: {data.get('sofa_qty', 0)}
  * Beds: {data.get('bed_qty', 0)}
  * Dining Tables: {data.get('dining_table_qty', 0)}
  * Chairs: {data.get('chairs_qty', 0)}
  * Lighting fixtures: {data.get('lights_qty', 0)}
  * Ceiling Fans: {data.get('ceiling_fan_qty', 0)}
  * Curtains: {data.get('curtains_qty', 0)}
  * Storage/Wardrobes: {data.get('storage_qty', 0)}
  * Decor pieces: {data.get('decor_qty', 0)}
- Custom Notes: {data.get('custom_requirements', 'None')}

CRITICAL INSTRUCTIONS:
1. Allocate the budget across key categories: Furniture, Lighting, Decor, Storage, Other, Reserve (contingency fund, 5-10%).
   The sum of allocated percentages MUST equal 100%.
2. Recommend 4 to 8 specific realistic product types/models matching the style and budget.
3. For each recommended item:
   - Provide an estimated realistic price. The sum of all recommended product prices MUST be within the total budget!
   - Recommend a real platform (e.g. Amazon, Flipkart, Pepperfry, Urban Ladder, IKEA).
   - Give a compelling practical reason why it fits the budget and aesthetic.
4. Output STRICT JSON only with NO markdown wrapper (or within a ```json codeblock).

JSON Structure:
{{
  "allocations": [
    {{"category": "Furniture", "allocated_amount": 20000, "percentage": 40, "notes": "Main seating and tables"}},
    {{"category": "Lighting", "allocated_amount": 7500, "percentage": 15, "notes": "Warm ambient and accent lights"}},
    {{"category": "Decor", "allocated_amount": 7500, "percentage": 15, "notes": "Rugs, wall art, plants"}},
    {{"category": "Storage", "allocated_amount": 7500, "percentage": 15, "notes": "Shelves and organizers"}},
    {{"category": "Other & Delivery", "allocated_amount": 3500, "percentage": 7, "notes": "Hardware and installation"}},
    {{"category": "Reserve", "allocated_amount": 4000, "percentage": 8, "notes": "Contingency reserve"}}
  ],
  "recommendations": [
    {{
      "product_name": "Modern 3-Seater Fabric Sofa",
      "category": "Furniture",
      "estimated_price": 18000,
      "reason": "Fits the modern aesthetic while keeping the furniture allocation within budget.",
      "style": "Modern",
      "color_or_material": "Grey Linen Fabric",
      "platform": "Amazon",
      "search_query": "Modern 3 Seater Fabric Sofa Grey"
    }}
  ],
  "ai_notes": "Expert interior budgeting tips for this style and space."
}}
"""


def build_party_prompt(data: dict) -> str:
    """Prompt for Gemini to dynamically allocate party budget and generate recommendations."""
    return f"""
You are an expert event planner and budget strategist for PocketSmart AI.
Analyze the following event details to generate an optimal, realistic budget breakdown and recommendations.

Event Details:
- Total Budget: {data.get('currency', '₹')}{data.get('budget')}
- Event Type: {data.get('event_type')}
- Number of Guests: {data.get('guest_count')}
- Location: {data.get('location')}
- Venue Preference: {data.get('venue_requirement')}
- Food Preference: {data.get('food_preference')}
- Decoration Level: {data.get('decoration_level')}
- Entertainment: {data.get('entertainment')}
- Additional Requirements: {data.get('additional_requirements', 'None')}

CRITICAL INSTRUCTIONS:
1. DO NOT hardcode fixed percentages. Dynamically adapt percentages based on guest count, event type, and location.
   Categories should typically include: Food & Catering, Venue & Setup, Decoration, Entertainment & Music, Miscellaneous / Reserve.
   Total percentage MUST sum to 100%.
2. Recommend 4 to 8 specific service/vendor/product items.
3. For each recommended item:
   - Provide an estimated realistic price. Total recommended cost must fit within the budget.
   - Specify appropriate platforms/vendors (e.g. Swiggy, Zomato, OYO, Amazon, Flipkart, Local Event Services).
   - Clear justification of why it fits this specific guest count and theme.
4. Output STRICT JSON only.

JSON Structure:
{{
  "cost_per_guest": 450.0,
  "allocations": [
    {{"category": "Food & Catering", "allocated_amount": 20000, "percentage": 40, "notes": "Full meal catering"}},
    {{"category": "Venue & Space", "allocated_amount": 12500, "percentage": 25, "notes": "Hall rental or venue booking"}},
    {{"category": "Decoration", "allocated_amount": 7500, "percentage": 15, "notes": "Theme backdrop & balloons/flowers"}},
    {{"category": "Entertainment & Sound", "allocated_amount": 5000, "percentage": 10, "notes": "Music system or host"}},
    {{"category": "Reserve & Miscellaneous", "allocated_amount": 5000, "percentage": 10, "notes": "Contingency & disposables"}}
  ],
  "recommendations": [
    {{
      "product_name": "Party Buffet Catering Package",
      "category": "Food & Catering",
      "estimated_price": 18000,
      "reason": "Provides delicious variety tailored for guests within per-plate budget limits.",
      "style": "Standard Buffet",
      "color_or_material": "Vegetarian & Non-Veg",
      "platform": "Zomato",
      "search_query": "Party Catering food bulk order"
    }}
  ],
  "ai_notes": "Key tips to maximize guest experience without exceeding the budget."
}}
"""


def build_jewelry_prompt(data: dict, has_image: bool = False) -> str:
    """Prompt for Gemini to analyze jewelry requirements (and optional outfit image)."""
    image_clause = ""
    if has_image:
        image_clause = """
An outfit image has been provided.
Analyze the image carefully to identify:
1. Dominant colors in the outfit.
2. The outfit style and silhouette (e.g., Silk Saree, Lehenga, Western Evening Gown, Indo-Western, Kurti).
3. Level of formality (e.g., Grand Festive, Black Tie, Cocktail, Casual).
4. Best matching jewelry style, metals, stones, and pearls that complement the neckline and colors.
Do NOT attempt to identify or name any person in the photo.
"""

    return f"""
You are a luxury fashion stylist and jewelry budget specialist for PocketSmart AI.
Analyze the user's jewelry requirements and provide recommendations that fit their budget.

Input:
- Budget: {data.get('currency', '₹')}{data.get('budget')}
- Occasion: {data.get('occasion')}
- Preferred Style: {data.get('style')}
- Jewelry Type: {data.get('jewelry_type')}
- Preferred Color / Material: {data.get('preferred_color_material', 'Not specified')}
- Outfit Description: {data.get('outfit_description', 'Not provided')}
{image_clause}

CRITICAL INSTRUCTIONS:
1. Provide a detailed outfit analysis (or inferred analysis if text only).
2. Recommend 3 to 6 curated jewelry pieces (e.g. choker, statement earrings, rings, bangles, or coordinated sets).
3. The total estimated price of the recommended pieces must be within the specified budget.
4. Recommend reputable platforms (e.g. Tanishq, CaratLane, Myntra, Amazon, Nykaa Fashion, Flipkart).
5. Output STRICT JSON only.

JSON Structure:
{{
  "outfit_analysis": {{
    "dominant_colors": ["Maroon", "Gold"],
    "outfit_style": "Traditional Banarasi Silk Saree",
    "formality": "High Traditional Wedding",
    "suitable_jewelry_style": "Temple or Kundan Heritage Jewelry",
    "suitable_metal_or_gems": "Antique Yellow Gold with Emerald Accents",
    "styling_advice": "Pair a high-neck blouse with a longer pendant necklace or statement jhumkas to avoid overcrowding the neckline."
  }},
  "recommendations": [
    {{
      "product_name": "Kundan Heritage Choker Necklace Set",
      "category": "Necklace",
      "estimated_price": 12500,
      "reason": "Complements the rich gold zari of the saree while staying well within the total budget.",
      "style": "Heritage Kundan",
      "color_or_material": "Gold-plated brass with green bead drops",
      "platform": "Myntra",
      "search_query": "Kundan Choker Necklace Set Green Gold"
    }}
  ],
  "ai_notes": "Styling advice on how to care for and wear these pieces."
}}
"""
