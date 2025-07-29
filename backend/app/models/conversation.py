from sqlalchemy import String, Boolean, DateTime, Text, JSON, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional, List
from datetime import datetime
import uuid

from ..database import Base


class Conversation(Base):
    __tablename__ = "conversations"
    
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Conversation metadata
    language: Mapped[str] = mapped_column(String(10), default="ar")
    status: Mapped[str] = mapped_column(String(20), default="active")  # active, archived, deleted
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    agent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("ai_agents.id", ondelete="SET NULL"), nullable=True)
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True)
    
    # Conversation settings
    settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    conversation_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    last_message_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    agent = relationship("AIAgent", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id}, agent_id={self.agent_id})>"
    
    @property
    def display_title(self) -> str:
        """Get display title for the conversation"""
        if self.title:
            return self.title
        elif self.summary:
            return self.summary[:50] + "..." if len(self.summary) > 50 else self.summary
        else:
            return f"Conversation {self.id}"


class Message(Base):
    __tablename__ = "messages"
    
    content: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user, assistant, system
    message_type: Mapped[str] = mapped_column(String(20), default="text")  # text, image, file, etc.
    
    # Message metadata
    language: Mapped[str] = mapped_column(String(10), default="ar")
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    processing_time: Mapped[Optional[float]] = mapped_column(nullable=True)
    
    # Relationships
    conversation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Message content and attachments
    attachments: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    message_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    user = relationship("User")
    
    def __repr__(self):
        return f"<Message(id={self.id}, conversation_id={self.conversation_id}, role={self.role})>"
    
    @property
    def preview(self) -> str:
        """Get a preview of the message content"""
        if len(self.content) > 100:
            return self.content[:100] + "..."
        return self.content