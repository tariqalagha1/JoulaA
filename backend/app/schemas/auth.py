from pydantic import BaseModel, EmailStr, validator
from typing import Optional
import re


class UserLogin(BaseModel):
    email_or_username: str
    password: str
    
    @validator('email_or_username')
    def validate_email_or_username(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('البريد الإلكتروني أو اسم المستخدم مطلوب')
        return v.strip()
    
    @validator('password')
    def validate_password(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('كلمة المرور مطلوبة')
        return v


class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name_ar: Optional[str] = None
    full_name_en: Optional[str] = None
    language_preference: Optional[str] = "ar"
    timezone: Optional[str] = "Asia/Riyadh"
    
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
    
    @validator('password')
    def validate_password(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('كلمة المرور مطلوبة')
        if len(v) < 8:
            raise ValueError('كلمة المرور يجب أن تكون 8 أحرف على الأقل')
        return v
    
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


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: Optional[dict] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    
    @validator('current_password')
    def validate_current_password(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('كلمة المرور الحالية مطلوبة')
        return v
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('كلمة المرور الجديدة مطلوبة')
        if len(v) < 8:
            raise ValueError('كلمة المرور الجديدة يجب أن تكون 8 أحرف على الأقل')
        return v


class PasswordReset(BaseModel):
    email: EmailStr
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('كلمة المرور الجديدة مطلوبة')
        if len(v) < 8:
            raise ValueError('كلمة المرور الجديدة يجب أن تكون 8 أحرف على الأقل')
        return v


class UserProfile(BaseModel):
    full_name_ar: Optional[str] = None
    full_name_en: Optional[str] = None
    language_preference: Optional[str] = "ar"
    timezone: Optional[str] = "Asia/Riyadh"
    
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


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name_ar: Optional[str] = None
    full_name_en: Optional[str] = None
    role: str
    language_preference: str
    timezone: str
    is_verified: bool
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True 