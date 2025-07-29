from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID
from enum import Enum

from ..models.agent import AgentType, AgentStatus, AgentCapability


class AgentBase(BaseModel):
    """Base schema for AI agents"""
    name_ar: str = Field(..., min_length=1, max_length=255, description="Agent name in Arabic")
    name_en: Optional[str] = Field(None, max_length=255, description="Agent name in English")
    description_ar: Optional[str] = Field(None, description="Agent description in Arabic")
    description_en: Optional[str] = Field(None, description="Agent description in English")
    agent_type: AgentType = Field(..., description="Type of the agent")
    capabilities: List[AgentCapability] = Field(default_factory=list, description="Agent capabilities")
    
    @validator('name_ar')
    def validate_name_ar(cls, v):
        if not v or not v.strip():
            raise ValueError('Arabic name is required')
        return v.strip()


class AgentConfigurationSchema(BaseModel):
    """Schema for agent configuration"""
    llm_provider: str = Field(default="anthropic", description="LLM provider")
    llm_model: str = Field(default="claude-3-sonnet", description="LLM model")
    system_prompt_ar: Optional[str] = Field(None, description="System prompt in Arabic")
    system_prompt_en: Optional[str] = Field(None, description="System prompt in English")
    max_tokens: int = Field(default=4000, ge=100, le=8000, description="Maximum tokens")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="LLM temperature")
    
    # Advanced configuration
    response_format: str = Field(default="text", description="Response format (text, json, markdown)")
    enable_memory: bool = Field(default=True, description="Enable conversation memory")
    memory_window: int = Field(default=10, ge=1, le=50, description="Number of previous messages to remember")
    
    # Arabic-specific settings
    arabic_preprocessing: bool = Field(default=True, description="Enable Arabic text preprocessing")
    rtl_formatting: bool = Field(default=True, description="Enable RTL text formatting")
    arabic_numerals: bool = Field(default=True, description="Use Arabic numerals in responses")


class AgentIntegrationSchema(BaseModel):
    """Schema for agent integrations"""
    type: str = Field(..., description="Integration type (sap, oracle, custom, etc.)")
    name: str = Field(..., description="Integration name")
    endpoint: Optional[str] = Field(None, description="API endpoint")
    authentication: Dict[str, Any] = Field(default_factory=dict, description="Authentication configuration")
    configuration: Dict[str, Any] = Field(default_factory=dict, description="Integration-specific configuration")
    is_active: bool = Field(default=True, description="Whether integration is active")


class AgentPermissionsSchema(BaseModel):
    """Schema for agent permissions"""
    can_read_data: bool = Field(default=True, description="Can read enterprise data")
    can_write_data: bool = Field(default=False, description="Can write/modify enterprise data")
    can_execute_actions: bool = Field(default=False, description="Can execute system actions")
    can_send_notifications: bool = Field(default=True, description="Can send notifications")
    can_access_external_apis: bool = Field(default=False, description="Can access external APIs")
    
    # Data access permissions
    accessible_data_types: List[str] = Field(default_factory=list, description="Types of data agent can access")
    restricted_data_types: List[str] = Field(default_factory=list, description="Types of data agent cannot access")
    
    # Action permissions
    allowed_actions: List[str] = Field(default_factory=list, description="Specific actions agent can perform")
    forbidden_actions: List[str] = Field(default_factory=list, description="Actions agent cannot perform")


class AgentCreate(AgentBase):
    """Schema for creating a new agent"""
    configuration: Optional[AgentConfigurationSchema] = Field(default_factory=AgentConfigurationSchema)
    integrations: List[AgentIntegrationSchema] = Field(default_factory=list)
    permissions: Optional[AgentPermissionsSchema] = Field(default_factory=AgentPermissionsSchema)
    prompt_templates: Dict[str, str] = Field(default_factory=dict, description="Prompt templates")
    response_templates: Dict[str, str] = Field(default_factory=dict, description="Response templates")
    is_public: bool = Field(default=False, description="Whether agent is public")


class AgentUpdate(BaseModel):
    """Schema for updating an agent"""
    name_ar: Optional[str] = Field(None, min_length=1, max_length=255)
    name_en: Optional[str] = Field(None, max_length=255)
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    status: Optional[AgentStatus] = None
    capabilities: Optional[List[AgentCapability]] = None
    configuration: Optional[Dict[str, Any]] = None
    integrations: Optional[List[AgentIntegrationSchema]] = None
    permissions: Optional[AgentPermissionsSchema] = None
    prompt_templates: Optional[Dict[str, str]] = None
    response_templates: Optional[Dict[str, str]] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None


class AgentResponse(AgentBase):
    """Schema for agent response"""
    id: UUID
    status: AgentStatus
    version: str
    is_active: bool
    is_public: bool
    organization_id: Optional[UUID]
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime]
    
    # Configuration (simplified for response)
    llm_provider: str
    llm_model: str
    max_tokens: int
    temperature: float
    
    # Metrics
    total_conversations: int = 0
    total_messages: int = 0
    success_rate: float = 0.0
    user_satisfaction_score: float = 0.0
    
    class Config:
        from_attributes = True


class AgentDetailResponse(AgentResponse):
    """Detailed schema for agent response with full configuration"""
    configuration: Dict[str, Any]
    integrations: List[Dict[str, Any]]
    permissions: Dict[str, Any]
    prompt_templates: Dict[str, str]
    response_templates: Dict[str, str]
    api_endpoints: Dict[str, Any]


class AgentListResponse(BaseModel):
    """Schema for agent list response"""
    agents: List[AgentResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class AgentMetricsResponse(BaseModel):
    """Schema for agent metrics response"""
    agent_id: UUID
    total_conversations: int
    total_messages: int
    total_tokens_used: int
    average_response_time: float
    success_rate: float
    user_satisfaction_score: float
    error_rate: float
    metrics_date: datetime
    period_type: str
    detailed_metrics: Dict[str, Any]


class AgentTemplateResponse(BaseModel):
    """Schema for agent template response"""
    id: UUID
    name_ar: str
    name_en: Optional[str]
    description_ar: Optional[str]
    description_en: Optional[str]
    agent_type: AgentType
    category: Optional[str]
    tags: List[str]
    difficulty_level: str
    usage_count: int
    rating: float
    is_featured: bool
    requires_premium: bool
    template_config: Dict[str, Any]
    
    class Config:
        from_attributes = True


class AgentWorkflowSchema(BaseModel):
    """Schema for agent workflows"""
    name_ar: str = Field(..., min_length=1, max_length=255)
    name_en: Optional[str] = Field(None, max_length=255)
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    workflow_steps: List[Dict[str, Any]] = Field(..., description="Ordered workflow steps")
    triggers: List[Dict[str, Any]] = Field(default_factory=list, description="Workflow triggers")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Execution conditions")
    auto_execute: bool = Field(default=False, description="Auto-execute workflow")
    max_execution_time: int = Field(default=300, ge=10, le=3600, description="Max execution time in seconds")


class AgentWorkflowResponse(AgentWorkflowSchema):
    """Schema for agent workflow response"""
    id: UUID
    agent_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AgentChatRequest(BaseModel):
    """Schema for agent chat requests"""
    message: str = Field(..., min_length=1, max_length=4000, description="User message")
    language: str = Field(default="ar", description="Message language (ar, en)")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    conversation_id: Optional[UUID] = Field(None, description="Existing conversation ID")
    stream: bool = Field(default=False, description="Stream response")
    
    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()


class AgentChatResponse(BaseModel):
    """Schema for agent chat responses"""
    message: str
    language: str
    conversation_id: UUID
    message_id: UUID
    agent_id: UUID
    response_time: float
    tokens_used: int
    confidence_score: Optional[float] = None
    suggested_actions: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class AgentActionRequest(BaseModel):
    """Schema for agent action requests"""
    action_type: str = Field(..., description="Type of action to perform")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    confirmation_required: bool = Field(default=True, description="Whether user confirmation is required")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Action context")


class AgentActionResponse(BaseModel):
    """Schema for agent action responses"""
    action_id: UUID
    action_type: str
    status: str  # pending, executing, completed, failed
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class AgentSearchRequest(BaseModel):
    """Schema for agent search requests"""
    query: Optional[str] = Field(None, description="Search query")
    agent_type: Optional[AgentType] = Field(None, description="Filter by agent type")
    capabilities: Optional[List[AgentCapability]] = Field(None, description="Filter by capabilities")
    is_public: Optional[bool] = Field(None, description="Filter by public/private")
    is_active: Optional[bool] = Field(True, description="Filter by active status")
    created_by: Optional[UUID] = Field(None, description="Filter by creator")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    
    # Pagination
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Page size")
    
    # Sorting
    sort_by: str = Field(default="created_at", description="Sort field")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="Sort order")


class BulkAgentOperation(BaseModel):
    """Schema for bulk agent operations"""
    agent_ids: List[UUID] = Field(..., min_items=1, max_items=100, description="List of agent IDs")
    operation: str = Field(..., description="Operation to perform (activate, deactivate, delete)")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Operation parameters")


class BulkAgentOperationResponse(BaseModel):
    """Schema for bulk agent operation responses"""
    operation: str
    total_requested: int
    successful: int
    failed: int
    results: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]