from sqlalchemy import String, Boolean, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional, List
from datetime import datetime
import uuid

from ..database import Base


class User(Base):
    __tablename__ = "users"
    
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    full_name_ar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Arabic name
    full_name_en: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # English name
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[str] = mapped_column(String(50), default="user")
    language_preference: Mapped[str] = mapped_column(String(10), default="ar")
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Riyadh")
    
    # Additional user profile fields
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    bio_ar: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bio_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Security fields
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_login_attempts: Mapped[int] = mapped_column(default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    password_reset_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    password_reset_expires: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    email_verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Preferences
    notification_preferences: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ui_preferences: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Relationships
    organizations = relationship("UserOrganization", back_populates="user")
    created_agents = relationship("AIAgent", foreign_keys="AIAgent.created_by")
    conversations = relationship("Conversation", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
    
    @property
    def display_name(self) -> str:
        """Get display name based on language preference"""
        if self.language_preference == "ar" and self.full_name_ar:
            return self.full_name_ar
        elif self.full_name_en:
            return self.full_name_en
        else:
            return self.username
    
    def to_dict(self) -> dict:
        """Convert user to dictionary"""
        return {
            "id": str(self.id),
            "email": self.email,
            "username": self.username,
            "full_name_ar": self.full_name_ar,
            "full_name_en": self.full_name_en,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "role": self.role,
            "language_preference": self.language_preference,
            "timezone": self.timezone,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }