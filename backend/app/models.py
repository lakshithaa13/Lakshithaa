from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    recommendations = relationship(
        "RecommendationHistory",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="desc(RecommendationHistory.created_at)"
    )

    def __repr__(self):
        return f"<User id={self.id} email='{self.email}' name='{self.name}'>"


class RecommendationHistory(Base):
    __tablename__ = "recommendation_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    planner_type = Column(String(50), nullable=False, index=True)  # 'home', 'party', 'jewelry'
    budget = Column(Float, nullable=False)
    currency = Column(String(10), default="₹", nullable=False)
    input_summary = Column(Text, nullable=False)
    result_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationship
    user = relationship("User", back_populates="recommendations")

    def __repr__(self):
        return f"<RecommendationHistory id={self.id} user_id={self.user_id} planner='{self.planner_type}' budget={self.budget}>"
