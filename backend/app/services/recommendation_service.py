import json
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models import RecommendationHistory, User
from app.services.gemini_service import (
    generate_home_recommendations,
    generate_party_recommendations,
    generate_jewelry_recommendations,
)

logger = logging.getLogger("pocketsmart.recommendation")


def save_history_record(
    db: Session,
    user: Optional[User],
    planner_type: str,
    budget: float,
    currency: str,
    input_summary: str,
    result_data: Dict[str, Any]
) -> Optional[RecommendationHistory]:
    """Persist recommendation plan into database if user is authenticated."""
    if not user:
        return None

    try:
        record = RecommendationHistory(
            user_id=user.id,
            planner_type=planner_type,
            budget=budget,
            currency=currency,
            input_summary=input_summary,
            result_json=json.dumps(result_data)
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save recommendation history: {e}")
        return None


def process_home_plan(
    data: Dict[str, Any],
    db: Session,
    user: Optional[User] = None
) -> Dict[str, Any]:
    """Execute complete Home Planning workflow and save history."""
    result = generate_home_recommendations(data)
    
    currency = data.get("currency", "₹")
    budget = float(data.get("budget", 0))
    room_type = data.get("room_type", "Home")
    style = data.get("style", "Modern")

    summary = f"{room_type} • {style} Style • {currency}{budget:,.0f}"
    
    history_record = save_history_record(
        db=db,
        user=user,
        planner_type="home",
        budget=budget,
        currency=currency,
        input_summary=summary,
        result_data=result
    )

    if history_record:
        result["history_id"] = history_record.id

    return result


def process_party_plan(
    data: Dict[str, Any],
    db: Session,
    user: Optional[User] = None
) -> Dict[str, Any]:
    """Execute complete Party Planning workflow and save history."""
    result = generate_party_recommendations(data)

    currency = data.get("currency", "₹")
    budget = float(data.get("budget", 0))
    event_type = data.get("event_type", "Party")
    guest_count = data.get("guest_count", 0)

    summary = f"{event_type} • {guest_count} Guests • {currency}{budget:,.0f}"

    history_record = save_history_record(
        db=db,
        user=user,
        planner_type="party",
        budget=budget,
        currency=currency,
        input_summary=summary,
        result_data=result
    )

    if history_record:
        result["history_id"] = history_record.id

    return result


def process_jewelry_plan(
    data: Dict[str, Any],
    db: Session,
    user: Optional[User] = None,
    image_path: Optional[str] = None
) -> Dict[str, Any]:
    """Execute complete Jewelry Planning workflow and save history."""
    result = generate_jewelry_recommendations(data, image_path=image_path)

    currency = data.get("currency", "₹")
    budget = float(data.get("budget", 0))
    occasion = data.get("occasion", "Occasion")
    jewelry_type = data.get("jewelry_type", "Jewelry")

    summary = f"{occasion} • {jewelry_type} • {currency}{budget:,.0f}"

    history_record = save_history_record(
        db=db,
        user=user,
        planner_type="jewelry",
        budget=budget,
        currency=currency,
        input_summary=summary,
        result_data=result
    )

    if history_record:
        result["history_id"] = history_record.id

    return result
