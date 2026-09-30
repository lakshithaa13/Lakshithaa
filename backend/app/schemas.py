from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field


# -------------------------------------------------------------
# User & Auth Schemas
# -------------------------------------------------------------

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    confirm_password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None


# -------------------------------------------------------------
# Common Recommendation Item Schema
# -------------------------------------------------------------

class BudgetItem(BaseModel):
    category: str
    allocated_amount: float
    percentage: float
    notes: Optional[str] = None


class RecommendationItem(BaseModel):
    product_name: str
    category: str
    estimated_price: float
    reason: str
    style: Optional[str] = None
    color_or_material: Optional[str] = None
    platform: str  # e.g., Amazon, Flipkart, Pepperfry, Urban Ladder, Myntra, Tanishq
    search_url: str


# -------------------------------------------------------------
# Home Interior Planner Schemas
# -------------------------------------------------------------

class HomePlannerInput(BaseModel):
    budget: float = Field(..., gt=0, description="Total budget in selected currency")
    currency: str = Field(default="₹")
    room_type: str = Field(..., description="Living Room, Bedroom, Kitchen, Dining Room, Multiple Rooms")
    style: str = Field(..., description="Modern, Minimalist, Traditional, Luxury, Scandinavian, Budget Friendly")
    sofa_qty: int = Field(default=0, ge=0)
    bed_qty: int = Field(default=0, ge=0)
    dining_table_qty: int = Field(default=0, ge=0)
    chairs_qty: int = Field(default=0, ge=0)
    lights_qty: int = Field(default=0, ge=0)
    ceiling_fan_qty: int = Field(default=0, ge=0)
    curtains_qty: int = Field(default=0, ge=0)
    storage_qty: int = Field(default=0, ge=0)
    decor_qty: int = Field(default=0, ge=0)
    custom_requirements: Optional[str] = None


class HomePlannerResult(BaseModel):
    planner_type: str = "home"
    total_budget: float
    currency: str
    total_estimated: float
    remaining_reserve: float
    allocations: List[BudgetItem]
    recommendations: List[RecommendationItem]
    is_fallback: bool = False
    ai_notes: Optional[str] = None


# -------------------------------------------------------------
# Party Planner Schemas
# -------------------------------------------------------------

class PartyPlannerInput(BaseModel):
    budget: float = Field(..., gt=0)
    currency: str = Field(default="₹")
    event_type: str = Field(..., description="Birthday, Wedding, Engagement, Anniversary, Corporate, College Event, Other")
    guest_count: int = Field(..., gt=0)
    location: str = Field(..., min_length=2)
    venue_requirement: str = Field(default="Needed", description="Needed, At Home, Outdoor, Booked Hall")
    food_preference: str = Field(..., description="Vegetarian, Non-Vegetarian, Both")
    decoration_level: str = Field(default="Standard", description="Basic, Standard, Premium")
    entertainment: str = Field(default="Basic", description="None, Basic, Premium")
    additional_requirements: Optional[str] = None


class PartyPlannerResult(BaseModel):
    planner_type: str = "party"
    total_budget: float
    currency: str
    event_type: str
    guest_count: int
    cost_per_guest: float
    total_estimated: float
    remaining_reserve: float
    allocations: List[BudgetItem]
    recommendations: List[RecommendationItem]
    is_fallback: bool = False
    ai_notes: Optional[str] = None


# -------------------------------------------------------------
# Jewelry Planner Schemas
# -------------------------------------------------------------

class JewelryPlannerInput(BaseModel):
    budget: float = Field(..., gt=0)
    currency: str = Field(default="₹")
    occasion: str = Field(..., description="Wedding, Engagement, Birthday, Festival, College Event, Party, Casual")
    style: str = Field(..., description="Traditional, Modern, Minimal, Statement, Elegant")
    jewelry_type: str = Field(..., description="Necklace, Earrings, Bangles, Bracelet, Ring, Full Set")
    preferred_color_material: Optional[str] = None
    outfit_description: Optional[str] = None


class OutfitAnalysis(BaseModel):
    dominant_colors: List[str] = []
    outfit_style: str = "Not specified"
    formality: str = "Semi-Formal"
    suitable_jewelry_style: str = "Modern & Elegant"
    suitable_metal_or_gems: str = "Gold / Kundan / Pearl"
    styling_advice: str = ""


class JewelryPlannerResult(BaseModel):
    planner_type: str = "jewelry"
    total_budget: float
    currency: str
    occasion: str
    total_estimated: float
    remaining_reserve: float
    outfit_analysis: Optional[OutfitAnalysis] = None
    recommendations: List[RecommendationItem]
    is_fallback: bool = False
    ai_notes: Optional[str] = None


# -------------------------------------------------------------
# History Schemas
# -------------------------------------------------------------

class HistoryItemResponse(BaseModel):
    id: int
    planner_type: str
    budget: float
    currency: str
    input_summary: str
    created_at: datetime
    result_data: Dict[str, Any]

    class Config:
        from_attributes = True
