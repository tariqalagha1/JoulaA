from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum

from .user import UserResponse
from .agent import AgentResponse


class ConversationStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    AUDIO = "audio"
    VIDEO = "video"


# Message Schemas
class MessageBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000, description="Message content")
    role: MessageRole = Field(..., description="Message role")
    message_type: MessageType = Field(default=MessageType.TEXT, description="Message type")
    language: str = Field(default="ar", min_length=2, max_length=10, description="Message language")
    attachments: Optional[Dict[str, Any]] = Field(None, description="Message attachments")
    message_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional message metadata")

    @validator('language')
    def validate_language(cls, v):
        allowed_languages = ['ar', 'en', 'fr', 'es']
        if v not in allowed_languages:
            raise ValueError(f'Language must be one of: {", ".join(allowed_languages)}')
        return v


class MessageCreate(MessageBase):
    conversation_id: Optional[UUID] = Field(None, description="Conversation ID (optional for new conversations)")


class MessageUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=10000)
    message_type: Optional[MessageType] = None
    attachments: Optional[Dict[str, Any]] = None
    message_metadata: Optional[Dict[str, Any]] = None


class MessageResponse(MessageBase):
    id: UUID
    conversation_id: UUID
    user_id: Optional[UUID]
    tokens_used: Optional[int]
    processing_time: Optional[float]
    created_at: datetime
    updated_at: datetime
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True


# Conversation Schemas
class ConversationBase(BaseModel):
    title: Optional[str] = Field(None, max_length=255, description="Conversation title")
    summary: Optional[str] = Field(None, max_length=1000, description="Conversation summary")
    language: str = Field(default="ar", min_length=2, max_length=10, description="Conversation language")
    status: ConversationStatus = Field(default=ConversationStatus.ACTIVE, description="Conversation status")
    settings: Optional[Dict[str, Any]] = Field(None, description="Conversation settings")
    conversation_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional conversation metadata")

    @validator('language')
    def validate_language(cls, v):
        allowed_languages = ['ar', 'en', 'fr', 'es']
        if v not in allowed_languages:
            raise ValueError(f'Language must be one of: {", ".join(allowed_languages)}')
        return v


class ConversationCreate(ConversationBase):
    agent_id: Optional[UUID] = Field(None, description="AI Agent ID")
    organization_id: Optional[UUID] = Field(None, description="Organization ID")
    initial_message: Optional[str] = Field(None, description="Initial message to start conversation")


class ConversationUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    summary: Optional[str] = Field(None, max_length=1000)
    status: Optional[ConversationStatus] = None
    settings: Optional[Dict[str, Any]] = None
    conversation_metadata: Optional[Dict[str, Any]] = None


class ConversationResponse(ConversationBase):
    id: UUID
    user_id: UUID
    agent_id: Optional[UUID]
    organization_id: Optional[UUID]
    message_count: int
    started_at: datetime
    last_message_at: Optional[datetime]
    ended_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    display_title: str

    class Config:
        from_attributes = True


class ConversationDetailResponse(ConversationResponse):
    user: Optional[UserResponse] = None
    agent: Optional[AgentResponse] = None
    messages: List[MessageResponse] = Field(default_factory=list)
    recent_messages: List[MessageResponse] = Field(default_factory=list, description="Last 10 messages")


class ConversationListResponse(BaseModel):
    conversations: List[ConversationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class MessageListResponse(BaseModel):
    messages: List[MessageResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# Chat and Streaming Schemas
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000, description="User message")
    conversation_id: Optional[UUID] = Field(None, description="Existing conversation ID")
    agent_id: Optional[UUID] = Field(None, description="AI Agent ID")
    message_type: MessageType = Field(default=MessageType.TEXT, description="Message type")
    attachments: Optional[Dict[str, Any]] = Field(None, description="Message attachments")
    stream: bool = Field(default=False, description="Enable streaming response")
    language: str = Field(default="ar", description="Message language")


class ChatResponse(BaseModel):
    conversation_id: UUID
    user_message: MessageResponse
    assistant_message: MessageResponse
    conversation: ConversationResponse


class StreamChunk(BaseModel):
    conversation_id: UUID
    message_id: UUID
    content: str
    is_complete: bool = False
    tokens_used: Optional[int] = None
    processing_time: Optional[float] = None


# Conversation Statistics
class ConversationStats(BaseModel):
    total_conversations: int
    active_conversations: int
    archived_conversations: int
    total_messages: int
    average_messages_per_conversation: float
    most_used_agents: List[Dict[str, Any]]
    conversation_languages: Dict[str, int]
    daily_conversation_count: List[Dict[str, Any]]


# Bulk Operations
class BulkConversationOperation(BaseModel):
    conversation_ids: List[UUID] = Field(..., min_items=1, max_items=100)
    operation: str = Field(..., description="Operation type: archive, delete, restore")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Additional operation parameters")

    @validator('operation')
    def validate_operation(cls, v):
        allowed_operations = ['archive', 'delete', 'restore', 'export']
        if v not in allowed_operations:
            raise ValueError(f'Operation must be one of: {", ".join(allowed_operations)}')
        return v


class BulkConversationOperationResponse(BaseModel):
    operation: str
    total_requested: int
    successful: int
    failed: int
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    results: List[Dict[str, Any]] = Field(default_factory=list)


# Search and Filter
class ConversationSearchRequest(BaseModel):
    query: Optional[str] = Field(None, description="Search query")
    agent_id: Optional[UUID] = Field(None, description="Filter by agent")
    status: Optional[ConversationStatus] = Field(None, description="Filter by status")
    language: Optional[str] = Field(None, description="Filter by language")
    date_from: Optional[datetime] = Field(None, description="Filter conversations from date")
    date_to: Optional[datetime] = Field(None, description="Filter conversations to date")
    min_messages: Optional[int] = Field(None, ge=0, description="Minimum message count")
    max_messages: Optional[int] = Field(None, ge=0, description="Maximum message count")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort_by: str = Field(default="last_message_at", description="Sort field")
    sort_order: str = Field(default="desc", description="Sort order")

    @validator('sort_by')
    def validate_sort_by(cls, v):
        allowed_fields = ['created_at', 'updated_at', 'last_message_at', 'message_count', 'title']
        if v not in allowed_fields:
            raise ValueError(f'Sort field must be one of: {", ".join(allowed_fields)}')
        return v

    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v not in ['asc', 'desc']:
            raise ValueError('Sort order must be "asc" or "desc"')
        return v