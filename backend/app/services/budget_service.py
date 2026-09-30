from typing import List, Dict, Any, Tuple


def validate_budget(budget: float, min_budget: float = 100.0) -> float:
    """Validate that the budget is a positive number above minimum threshold."""
    if budget is None:
        raise ValueError("Budget is required.")
    try:
        val = float(budget)
    except (ValueError, TypeError):
        raise ValueError("Budget must be a valid number.")

    if val < min_budget:
        raise ValueError(f"Budget must be at least {min_budget:,.2f}.")
    if val > 100_000_000:
        raise ValueError("Budget exceeds the maximum supported limit (100,000,000).")
    return round(val, 2)


def allocate_home_budget(budget: float, room_type: str = "Living Room", style: str = "Modern", quantities: Dict[str, int] = None) -> List[Dict[str, Any]]:
    """
    Generate an intelligent budget breakdown for home interiors based on room type and requested quantities.
    Always sums to 100%.
    """
    total = validate_budget(budget)
    quantities = quantities or {}

    # Base allocations
    furn_pct = 45.0
    light_pct = 15.0
    decor_pct = 15.0
    storage_pct = 12.0
    other_pct = 5.0
    reserve_pct = 8.0

    # Adjust based on room type
    room_lower = (room_type or "").lower()
    if "bedroom" in room_lower:
        furn_pct = 40.0
        storage_pct = 22.0
        light_pct = 12.0
        decor_pct = 13.0
        other_pct = 5.0
        reserve_pct = 8.0
    elif "kitchen" in room_lower:
        storage_pct = 40.0
        furn_pct = 20.0
        light_pct = 18.0
        decor_pct = 7.0
        other_pct = 7.0
        reserve_pct = 8.0
    elif "dining" in room_lower:
        furn_pct = 50.0
        light_pct = 15.0
        decor_pct = 15.0
        storage_pct = 10.0
        other_pct = 3.0
        reserve_pct = 7.0

    allocations = [
        {
            "category": "Furniture",
            "percentage": furn_pct,
            "allocated_amount": round(total * (furn_pct / 100.0), 2),
            "notes": "Seating, tables, and core comfort pieces"
        },
        {
            "category": "Lighting",
            "percentage": light_pct,
            "allocated_amount": round(total * (light_pct / 100.0), 2),
            "notes": "Ceiling fixtures, ambient lamps, and accent lighting"
        },
        {
            "category": "Decor",
            "percentage": decor_pct,
            "allocated_amount": round(total * (decor_pct / 100.0), 2),
            "notes": "Rugs, wall art, curtains, and cushions"
        },
        {
            "category": "Storage",
            "percentage": storage_pct,
            "allocated_amount": round(total * (storage_pct / 100.0), 2),
            "notes": "Cabinets, shelves, and modular organizers"
        },
        {
            "category": "Other & Hardware",
            "percentage": other_pct,
            "allocated_amount": round(total * (other_pct / 100.0), 2),
            "notes": "Installation, delivery, and fittings"
        },
        {
            "category": "Reserve",
            "percentage": reserve_pct,
            "allocated_amount": round(total * (reserve_pct / 100.0), 2),
            "notes": "Contingency reserve for unexpected expenses"
        }
    ]

    return allocations


def allocate_party_budget(budget: float, guest_count: int, venue_req: str = "Needed", food_pref: str = "Both", decor_level: str = "Standard") -> List[Dict[str, Any]]:
    """
    Generate dynamic event budget allocation adapted to guest count, venue requirements, and decor level.
    """
    total = validate_budget(budget)
    guests = max(1, int(guest_count or 1))

    # Base percentages
    if venue_req and "home" in venue_req.lower():
        # Saving on venue means more budget for food and decor
        venue_pct = 5.0
        food_pct = 50.0
        decor_pct = 20.0
        entertainment_pct = 15.0
        misc_reserve_pct = 10.0
    else:
        venue_pct = 25.0
        food_pct = 40.0
        decor_pct = 15.0
        entertainment_pct = 10.0
        misc_reserve_pct = 10.0

    # Adjust for decor level
    if decor_level == "Premium":
        decor_pct += 5.0
        food_pct -= 3.0
        misc_reserve_pct -= 2.0
    elif decor_level == "Basic":
        decor_pct = max(8.0, decor_pct - 5.0)
        misc_reserve_pct += 5.0

    allocations = [
        {
            "category": "Food & Catering",
            "percentage": food_pct,
            "allocated_amount": round(total * (food_pct / 100.0), 2),
            "notes": f"Estimated ~{(total * food_pct / 100.0) / guests:,.0f} per guest catering budget"
        },
        {
            "category": "Venue & Space",
            "percentage": venue_pct,
            "allocated_amount": round(total * (venue_pct / 100.0), 2),
            "notes": "Venue hire, seating arrangements, and utilities"
        },
        {
            "category": "Decoration",
            "percentage": decor_pct,
            "allocated_amount": round(total * (decor_pct / 100.0), 2),
            "notes": f"{decor_level} styling, backdrop, lighting, and table centers"
        },
        {
            "category": "Entertainment & Music",
            "percentage": entertainment_pct,
            "allocated_amount": round(total * (entertainment_pct / 100.0), 2),
            "notes": "Sound system, DJ/host, and guest activities"
        },
        {
            "category": "Reserve & Miscellaneous",
            "percentage": misc_reserve_pct,
            "allocated_amount": round(total * (misc_reserve_pct / 100.0), 2),
            "notes": "Emergency contingency, tips, and incidentals"
        }
    ]

    return allocations


def enforce_budget_limit(recommendations: List[Dict[str, Any]], total_budget: float) -> Tuple[List[Dict[str, Any]], float, float]:
    """
    Ensure the sum of recommended products does not exceed total budget.
    Calculates total_estimated and remaining_reserve.
    """
    total_budget = float(total_budget)
    validated_items = []
    running_total = 0.0

    for item in recommendations:
        price = float(item.get("estimated_price", 0))
        if price <= 0:
            continue
        
        # If adding this item pushes us over the budget, scale or keep within bounds
        if running_total + price <= total_budget:
            validated_items.append(item)
            running_total += price
        else:
            # If we don't have enough items yet, adjust price or include if reasonable
            if len(validated_items) < 3 and total_budget > running_total:
                remaining_room = total_budget - running_total
                adjusted_item = dict(item)
                adjusted_item["estimated_price"] = round(remaining_room * 0.9, 2)
                adjusted_item["reason"] += " (Price adjusted to fit remaining budget balance)"
                validated_items.append(adjusted_item)
                running_total += adjusted_item["estimated_price"]
                break

    running_total = round(running_total, 2)
    remaining_reserve = round(max(0.0, total_budget - running_total), 2)
    return validated_items, running_total, remaining_reserve
