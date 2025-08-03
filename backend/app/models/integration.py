from sqlalchemy import String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from ..database import Base


class Integration(Base):
    """Model for enterprise integrations"""
    __tablename__ = "enterprise_integrations"
    
    # Basic information
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    integration_type: Mapped[str] = mapped_column(
        String(100), 
        nullable=False,
        index=True,
        comment="Integration type: sap, oracle, odoo, custom, etc."
    )
    
    name: Mapped[str] = mapped_column(
        String(255), 
        nullable=False,
        comment="Human-readable name for the integration"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="Description of the integration"
    )
    
    # Configuration
    configuration: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, 
        nullable=False,
        default=dict,
        comment="Integration-specific configuration including endpoints, auth, etc."
    )
    
    # Status and sync information
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        default=True,
        nullable=False,
        index=True
    )
    
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True,
        comment="Last successful synchronization timestamp"
    )
    
    sync_status: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True,
        default="pending",
        comment="Current sync status: pending, syncing, success, error"
    )
    
    sync_error: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="Last sync error message if any"
    )
    
    # Metadata
    metadata_: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        "metadata",
        JSONB, 
        nullable=True,
        default=dict,
        comment="Additional metadata for the integration"
    )
    
    # Health check
    health_check_url: Mapped[Optional[str]] = mapped_column(
        String(500), 
        nullable=True,
        comment="URL for health check endpoint"
    )
    
    last_health_check: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True,
        comment="Last health check timestamp"
    )
    
    health_status: Mapped[Optional[str]] = mapped_column(
        String(20), 
        nullable=True,
        default="unknown",
        comment="Health status: healthy, unhealthy, unknown"
    )
    
    # Relationships
    organization = relationship("Organization", back_populates="integrations")
    
    def __repr__(self) -> str:
        return f"<Integration(id={self.id}, name='{self.name}', type='{self.integration_type}', active={self.is_active})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert integration to dictionary"""
        return {
            "id": str(self.id),
            "organization_id": str(self.organization_id),
            "integration_type": self.integration_type,
            "name": self.name,
            "description": self.description,
            "configuration": self.configuration,
            "is_active": self.is_active,
            "last_sync_at": self.last_sync_at.isoformat() if self.last_sync_at else None,
            "sync_status": self.sync_status,
            "sync_error": self.sync_error,
            "metadata": self.metadata_,
            "health_check_url": self.health_check_url,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "health_status": self.health_status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @property
    def display_name(self) -> str:
        """Get display name for the integration"""
        return self.name or f"{self.integration_type.title()} Integration"
    
    @property
    def is_healthy(self) -> bool:
        """Check if integration is healthy"""
        return self.health_status == "healthy" and self.is_active
    
    @property
    def needs_sync(self) -> bool:
        """Check if integration needs synchronization"""
        if not self.is_active:
            return False
        
        if not self.last_sync_at:
            return True
        
        # Check if last sync was more than 1 hour ago
        from datetime import timedelta
        return (datetime.utcnow() - self.last_sync_at) > timedelta(hours=1)