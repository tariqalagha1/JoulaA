"""Organization schemas for Joulaa platform"""

from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class OrganizationBase(BaseModel):
    """Base organization schema"""
    name_ar: str = Field(..., min_length=1, max_length=255, description="Arabic name")
    name_en: Optional[str] = Field(None, max_length=255, description="English name")
    description_ar: Optional[str] = Field(None, description="Arabic description")
    description_en: Optional[str] = Field(None, description="English description")
    email: Optional[str] = Field(None, max_length=255, description="Contact email")
    phone: Optional[str] = Field(None, max_length=20, description="Contact phone")
    website: Optional[str] = Field(None, max_length=500, description="Website URL")
    address_ar: Optional[str] = Field(None, description="Arabic address")
    address_en: Optional[str] = Field(None, description="English address")
    city: Optional[str] = Field(None, max_length=100, description="City")
    country: str = Field("Saudi Arabia", max_length=100, description="Country")
    
    @validator('name_ar')
    def validate_name_ar(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('الاسم العربي مطلوب')
        return v.strip()
    
    @validator('email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('البريد الإلكتروني غير صحيح')
        return v


class OrganizationCreate(OrganizationBase):
    """Schema for creating a new organization"""
    subscription_plan: str = Field("basic", description="Subscription plan")
    max_users: int = Field(10, ge=1, le=1000, description="Maximum users")
    max_agents: int = Field(5, ge=1, le=100, description="Maximum agents")
    settings: Optional[Dict[str, Any]] = Field(None, description="Organization settings")
    
    @validator('subscription_plan')
    def validate_subscription_plan(cls, v):
        allowed_plans = ['basic', 'premium', 'enterprise']
        if v not in allowed_plans:
            raise ValueError(f'خطة الاشتراك يجب أن تكون واحدة من: {", ".join(allowed_plans)}')
        return v


class OrganizationUpdate(BaseModel):
    """Schema for updating organization information"""
    name_ar: Optional[str] = Field(None, min_length=1, max_length=255)
    name_en: Optional[str] = Field(None, max_length=255)
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=500)
    address_ar: Optional[str] = None
    address_en: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    subscription_plan: Optional[str] = None
    max_users: Optional[int] = Field(None, ge=1, le=1000)
    max_agents: Optional[int] = Field(None, ge=1, le=100)
    is_active: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None
    
    @validator('name_ar')
    def validate_name_ar(cls, v):
        if v is not None and (not v or len(v.strip()) == 0):
            raise ValueError('الاسم العربي لا يمكن أن يكون فارغاً')
        return v.strip() if v else None
    
    @validator('subscription_plan')
    def validate_subscription_plan(cls, v):
        if v is not None:
            allowed_plans = ['basic', 'premium', 'enterprise']
            if v not in allowed_plans:
                raise ValueError(f'خطة الاشتراك يجب أن تكون واحدة من: {", ".join(allowed_plans)}')
        return v


class OrganizationResponse(BaseModel):
    """Schema for organization response"""
    id: UUID
    name_ar: str
    name_en: Optional[str] = None
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address_ar: Optional[str] = None
    address_en: Optional[str] = None
    city: Optional[str] = None
    country: str
    subscription_plan: str
    max_users: int
    max_agents: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class OrganizationDetailResponse(OrganizationResponse):
    """Schema for detailed organization response"""
    settings: Optional[Dict[str, Any]] = None
    member_count: int = 0
    agent_count: int = 0
    members: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        from_attributes = True


class OrganizationListResponse(BaseModel):
    """Schema for organization list response"""
    organizations: List[OrganizationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class OrganizationMemberBase(BaseModel):
    """Base schema for organization member"""
    user_id: UUID
    role: str = Field("member", description="Member role")
    
    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['owner', 'admin', 'member', 'viewer']
        if v not in allowed_roles:
            raise ValueError(f'الدور يجب أن يكون واحداً من: {", ".join(allowed_roles)}')
        return v


class OrganizationMemberCreate(OrganizationMemberBase):
    """Schema for adding a member to organization"""
    pass


class OrganizationMemberUpdate(BaseModel):
    """Schema for updating organization member"""
    role: Optional[str] = None
    is_active: Optional[bool] = None
    
    @validator('role')
    def validate_role(cls, v):
        if v is not None:
            allowed_roles = ['owner', 'admin', 'member', 'viewer']
            if v not in allowed_roles:
                raise ValueError(f'الدور يجب أن يكون واحداً من: {", ".join(allowed_roles)}')
        return v


class OrganizationMemberResponse(BaseModel):
    """Schema for organization member response"""
    user_id: UUID
    organization_id: UUID
    role: str
    is_active: bool
    joined_at: datetime
    user: Optional[Dict[str, Any]] = None  # User details
    
    class Config:
        from_attributes = True


class OrganizationStats(BaseModel):
    """Schema for organization statistics"""
    total_members: int
    active_members: int
    total_agents: int
    active_agents: int
    total_conversations: int
    conversations_last_30_days: int
    storage_used: float  # in MB
    api_calls_last_30_days: int
    
    class Config:
        from_attributes = True


class OrganizationInvitation(BaseModel):
    """Schema for organization invitation"""
    email: str = Field(..., description="Email to invite")
    role: str = Field("member", description="Role for the invited user")
    message: Optional[str] = Field(None, description="Invitation message")
    expires_in_days: int = Field(7, ge=1, le=30, description="Invitation expiry in days")
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('البريد الإلكتروني غير صحيح')
        return v
    
    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['admin', 'member', 'viewer']
        if v not in allowed_roles:
            raise ValueError(f'الدور يجب أن يكون واحداً من: {", ".join(allowed_roles)}')
        return v


class OrganizationInvitationResponse(BaseModel):
    """Schema for organization invitation response"""
    id: UUID
    organization_id: UUID
    email: str
    role: str
    invited_by: UUID
    message: Optional[str] = None
    status: str  # pending, accepted, expired, cancelled
    expires_at: datetime
    created_at: datetime
    accepted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BulkMemberOperation(BaseModel):
    """Schema for bulk member operations"""
    user_ids: List[UUID] = Field(..., min_items=1, description="List of user IDs")
    operation: str = Field(..., description="Operation to perform")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Operation parameters")
    
    @validator('operation')
    def validate_operation(cls, v):
        allowed_operations = ['activate', 'deactivate', 'remove', 'update_role']
        if v not in allowed_operations:
            raise ValueError(f'العملية يجب أن تكون واحدة من: {", ".join(allowed_operations)}')
        return v


class BulkMemberOperationResponse(BaseModel):
    """Schema for bulk member operation response"""
    operation: str
    total_requested: int
    successful: int
    failed: int
    errors: List[Dict[str, Any]]
    results: List[Dict[str, Any]]