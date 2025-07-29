"""User schemas for Joulaa platform"""

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
import re


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str
    full_name_ar: Optional[str] = None
    full_name_en: Optional[str] = None
    language_preference: str = "ar"
    timezone: str = "Asia/Riyadh"
    
    @validator('username')
    def validate_username(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('اسم المستخدم مطلوب')
        if len(v) < 3:
            raise ValueError('اسم المستخدم يجب أن يكون 3 أحرف على الأقل')
        if len(v) > 50:
            raise ValueError('اسم المستخدم يجب أن يكون 50 حرف على الأكثر')
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('اسم المستخدم يجب أن يحتوي على أحرف إنجليزية وأرقام وشرطة سفلية فقط')
        return v.strip()
    
    @validator('full_name_ar')
    def validate_full_name_ar(cls, v):
        if v and len(v.strip()) > 255:
            raise ValueError('الاسم العربي يجب أن يكون 255 حرف على الأكثر')
        return v.strip() if v else None
    
    @validator('full_name_en')
    def validate_full_name_en(cls, v):
        if v and len(v.strip()) > 255:
            raise ValueError('الاسم الإنجليزي يجب أن يكون 255 حرف على الأكثر')
        return v.strip() if v else None
    
    @validator('language_preference')
    def validate_language_preference(cls, v):
        if v not in ['ar', 'en']:
            raise ValueError('اللغة المفضلة يجب أن تكون ar أو en')
        return v


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('كلمة المرور مطلوبة')
        if len(v) < 8:
            raise ValueError('كلمة المرور يجب أن تكون 8 أحرف على الأقل')
        if len(v) > 128:
            raise ValueError('كلمة المرور يجب أن تكون 128 حرف على الأكثر')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    full_name_ar: Optional[str] = None
    full_name_en: Optional[str] = None
    language_preference: Optional[str] = None
    timezone: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    phone_number: Optional[str] = None
    
    @validator('full_name_ar')
    def validate_full_name_ar(cls, v):
        if v and len(v.strip()) > 255:
            raise ValueError('الاسم العربي يجب أن يكون 255 حرف على الأكثر')
        return v.strip() if v else None
    
    @validator('full_name_en')
    def validate_full_name_en(cls, v):
        if v and len(v.strip()) > 255:
            raise ValueError('الاسم الإنجليزي يجب أن يكون 255 حرف على الأكثر')
        return v.strip() if v else None
    
    @validator('language_preference')
    def validate_language_preference(cls, v):
        if v and v not in ['ar', 'en']:
            raise ValueError('اللغة المفضلة يجب أن تكون ar أو en')
        return v
    
    @validator('bio')
    def validate_bio(cls, v):
        if v and len(v.strip()) > 500:
            raise ValueError('النبذة الشخصية يجب أن تكون 500 حرف على الأكثر')
        return v.strip() if v else None
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v and not re.match(r'^\+?[1-9]\d{1,14}$', v):
            raise ValueError('رقم الهاتف غير صحيح')
        return v


class UserResponse(BaseModel):
    """Schema for user response"""
    id: UUID
    email: str
    username: str
    full_name_ar: Optional[str] = None
    full_name_en: Optional[str] = None
    display_name: Optional[str] = None
    language_preference: str
    timezone: str
    role: str
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    """Schema for detailed user response with additional information"""
    failed_login_attempts: int
    locked_until: Optional[datetime] = None
    organizations: Optional[List[Dict[str, Any]]] = None
    preferences: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for paginated user list response"""
    users: List[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class UserPreferences(BaseModel):
    """Schema for user preferences"""
    theme: Optional[str] = "light"  # light, dark, auto
    notifications_email: bool = True
    notifications_push: bool = True
    notifications_sms: bool = False
    default_agent_language: str = "ar"
    auto_save_conversations: bool = True
    conversation_history_retention: int = 90  # days
    
    @validator('theme')
    def validate_theme(cls, v):
        if v not in ['light', 'dark', 'auto']:
            raise ValueError('المظهر يجب أن يكون light أو dark أو auto')
        return v
    
    @validator('default_agent_language')
    def validate_default_agent_language(cls, v):
        if v not in ['ar', 'en']:
            raise ValueError('لغة الوكيل الافتراضية يجب أن تكون ar أو en')
        return v
    
    @validator('conversation_history_retention')
    def validate_retention(cls, v):
        if v < 1 or v > 365:
            raise ValueError('مدة الاحتفاظ بالمحادثات يجب أن تكون بين 1 و 365 يوم')
        return v


class UserStats(BaseModel):
    """Schema for user statistics"""
    total_conversations: int
    total_agents_created: int
    total_organizations: int
    last_activity: Optional[datetime] = None
    most_used_agent: Optional[Dict[str, Any]] = None
    conversation_count_last_30_days: int
    average_conversation_length: float
    
    class Config:
        from_attributes = True


class UserActivityLog(BaseModel):
    """Schema for user activity log"""
    id: UUID
    user_id: UUID
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[UUID] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserInvitation(BaseModel):
    """Schema for user invitation"""
    email: EmailStr
    role: str = "user"
    organization_id: Optional[UUID] = None
    message: Optional[str] = None
    expires_in_days: int = 7
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ['user', 'admin', 'manager', 'viewer']:
            raise ValueError('الدور يجب أن يكون user أو admin أو manager أو viewer')
        return v
    
    @validator('expires_in_days')
    def validate_expires_in_days(cls, v):
        if v < 1 or v > 30:
            raise ValueError('مدة انتهاء الدعوة يجب أن تكون بين 1 و 30 يوم')
        return v


class UserInvitationResponse(BaseModel):
    """Schema for user invitation response"""
    id: UUID
    email: str
    role: str
    organization_id: Optional[UUID] = None
    invited_by: UUID
    message: Optional[str] = None
    status: str  # pending, accepted, expired, cancelled
    expires_at: datetime
    created_at: datetime
    accepted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BulkUserOperation(BaseModel):
    """Schema for bulk user operations"""
    user_ids: List[UUID]
    operation: str  # activate, deactivate, delete, update_role
    parameters: Optional[Dict[str, Any]] = None
    
    @validator('user_ids')
    def validate_user_ids(cls, v):
        if not v or len(v) == 0:
            raise ValueError('يجب تحديد مستخدم واحد على الأقل')
        if len(v) > 100:
            raise ValueError('لا يمكن تنفيذ العملية على أكثر من 100 مستخدم في المرة الواحدة')
        return v
    
    @validator('operation')
    def validate_operation(cls, v):
        if v not in ['activate', 'deactivate', 'delete', 'update_role']:
            raise ValueError('العملية يجب أن تكون activate أو deactivate أو delete أو update_role')
        return v


class BulkUserOperationResponse(BaseModel):
    """Schema for bulk user operation response"""
    operation: str
    total_requested: int
    successful: int
    failed: int
    errors: List[Dict[str, Any]]
    results: List[Dict[str, Any]]