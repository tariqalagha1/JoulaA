"""User service for Joulaa platform"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
import structlog

from ..models.user import User
from ..models.organization import Organization, OrganizationMember
from ..core.security import get_password_hash, verify_password
from ..core.config import settings
from ..core.exceptions import (
    UserNotFoundError, ValidationError, AuthenticationError
)
from ..schemas.user import UserCreate, UserUpdate

logger = structlog.get_logger()


class UserService:
    """Service for user management operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(
        self,
        email: str,
        username: str,
        password: str,
        full_name_ar: Optional[str] = None,
        full_name_en: Optional[str] = None,
        language_preference: str = "ar",
        timezone: str = "Asia/Riyadh",
        role: str = "user"
    ) -> User:
        """Create a new user"""
        
        try:
            # Check if user already exists
            existing_user = await self.get_user_by_email_or_username(email, username)
            if existing_user:
                if existing_user.email == email:
                    raise ValidationError("البريد الإلكتروني مستخدم بالفعل")
                else:
                    raise ValidationError("اسم المستخدم مستخدم بالفعل")
            
            # Create user
            user = User(
                email=email,
                username=username,
                password_hash=get_password_hash(password),
                full_name_ar=full_name_ar,
                full_name_en=full_name_en,
                display_name=full_name_ar or full_name_en or username,
                language_preference=language_preference,
                timezone=timezone,
                role=role,
                is_active=True,
                is_verified=False,
                verification_token=self._generate_token(),
                created_at=datetime.utcnow()
            )
            
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info(
                "User created successfully",
                user_id=str(user.id),
                email=email,
                username=username
            )
            
            return user
            
        except ValidationError:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Failed to create user",
                email=email,
                username=username,
                error=str(e),
                exc_info=True
            )
            raise
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        
        try:
            query = select(User).where(User.id == user_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(
                "Failed to get user by ID",
                user_id=str(user_id),
                error=str(e)
            )
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        
        try:
            query = select(User).where(User.email == email)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(
                "Failed to get user by email",
                email=email,
                error=str(e)
            )
            return None
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        
        try:
            query = select(User).where(User.username == username)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(
                "Failed to get user by username",
                username=username,
                error=str(e)
            )
            return None
    
    async def get_user_by_email_or_username(
        self, 
        email: str, 
        username: str
    ) -> Optional[User]:
        """Get user by email or username"""
        
        try:
            query = select(User).where(
                or_(User.email == email, User.username == username)
            )
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(
                "Failed to get user by email or username",
                email=email,
                username=username,
                error=str(e)
            )
            return None
    
    async def update_user(
        self, 
        user_id: UUID, 
        user_data: UserUpdate
    ) -> Optional[User]:
        """Update user information"""
        
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                raise UserNotFoundError("المستخدم غير موجود")
            
            # Update fields
            update_data = user_data.dict(exclude_unset=True)
            
            for field, value in update_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            
            user.updated_at = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info(
                "User updated successfully",
                user_id=str(user_id),
                updated_fields=list(update_data.keys())
            )
            
            return user
            
        except UserNotFoundError:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Failed to update user",
                user_id=str(user_id),
                error=str(e),
                exc_info=True
            )
            raise
    
    async def change_password(
        self, 
        user_id: UUID, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """Change user password"""
        
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                raise UserNotFoundError("المستخدم غير موجود")
            
            # Verify current password
            if not verify_password(current_password, user.password_hash):
                raise AuthenticationError("كلمة المرور الحالية غير صحيحة")
            
            # Update password
            user.password_hash = get_password_hash(new_password)
            user.updated_at = datetime.utcnow()
            
            # Clear any password reset tokens
            user.password_reset_token = None
            user.password_reset_expires = None
            
            await self.db.commit()
            
            logger.info(
                "Password changed successfully",
                user_id=str(user_id)
            )
            
            return True
            
        except (UserNotFoundError, AuthenticationError):
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Failed to change password",
                user_id=str(user_id),
                error=str(e),
                exc_info=True
            )
            return False
    
    async def generate_password_reset_token(self, user: User) -> str:
        """Generate password reset token"""
        
        try:
            reset_token = self._generate_token()
            
            user.password_reset_token = reset_token
            user.password_reset_expires = datetime.utcnow() + timedelta(hours=24)
            user.updated_at = datetime.utcnow()
            
            await self.db.commit()
            
            logger.info(
                "Password reset token generated",
                user_id=str(user.id)
            )
            
            return reset_token
            
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Failed to generate password reset token",
                user_id=str(user.id),
                error=str(e),
                exc_info=True
            )
            raise
    
    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password using token"""
        
        try:
            # Find user by reset token
            query = select(User).where(
                and_(
                    User.password_reset_token == token,
                    User.password_reset_expires > datetime.utcnow()
                )
            )
            result = await self.db.execute(query)
            user = result.scalar_one_or_none()
            
            if not user:
                return False
            
            # Update password and clear reset token
            user.password_hash = get_password_hash(new_password)
            user.password_reset_token = None
            user.password_reset_expires = None
            user.updated_at = datetime.utcnow()
            
            await self.db.commit()
            
            logger.info(
                "Password reset successfully",
                user_id=str(user.id)
            )
            
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Failed to reset password",
                token=token[:10] + "...",  # Log partial token for security
                error=str(e),
                exc_info=True
            )
            return False
    
    async def verify_email(self, token: str) -> bool:
        """Verify user email using token"""
        
        try:
            # Find user by verification token
            query = select(User).where(User.verification_token == token)
            result = await self.db.execute(query)
            user = result.scalar_one_or_none()
            
            if not user:
                return False
            
            # Mark as verified
            user.is_verified = True
            user.verification_token = None
            user.updated_at = datetime.utcnow()
            
            await self.db.commit()
            
            logger.info(
                "Email verified successfully",
                user_id=str(user.id)
            )
            
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Failed to verify email",
                token=token[:10] + "...",  # Log partial token for security
                error=str(e),
                exc_info=True
            )
            return False
    
    async def deactivate_user(self, user_id: UUID) -> bool:
        """Deactivate user account"""
        
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                raise UserNotFoundError("المستخدم غير موجود")
            
            user.is_active = False
            user.updated_at = datetime.utcnow()
            
            await self.db.commit()
            
            logger.info(
                "User deactivated successfully",
                user_id=str(user_id)
            )
            
            return True
            
        except UserNotFoundError:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Failed to deactivate user",
                user_id=str(user_id),
                error=str(e),
                exc_info=True
            )
            return False
    
    async def activate_user(self, user_id: UUID) -> bool:
        """Activate user account"""
        
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                raise UserNotFoundError("المستخدم غير موجود")
            
            user.is_active = True
            user.updated_at = datetime.utcnow()
            
            await self.db.commit()
            
            logger.info(
                "User activated successfully",
                user_id=str(user_id)
            )
            
            return True
            
        except UserNotFoundError:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Failed to activate user",
                user_id=str(user_id),
                error=str(e),
                exc_info=True
            )
            return False
    
    async def get_user_organizations(self, user_id: UUID) -> List[Organization]:
        """Get organizations user belongs to"""
        
        try:
            query = (
                select(Organization)
                .join(OrganizationMember)
                .where(OrganizationMember.user_id == user_id)
                .options(selectinload(Organization.members))
            )
            
            result = await self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(
                "Failed to get user organizations",
                user_id=str(user_id),
                error=str(e)
            )
            return []
    
    async def update_last_login(self, user_id: UUID) -> bool:
        """Update user's last login timestamp"""
        
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.last_login = datetime.utcnow()
            user.failed_login_attempts = 0  # Reset failed attempts on successful login
            user.locked_until = None  # Clear any account locks
            
            await self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(
                "Failed to update last login",
                user_id=str(user_id),
                error=str(e)
            )
            return False
    
    async def increment_failed_login_attempts(self, user_id: UUID) -> bool:
        """Increment failed login attempts and lock account if necessary"""
        
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.failed_login_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=30)
                logger.warning(
                    "User account locked due to failed login attempts",
                    user_id=str(user_id),
                    failed_attempts=user.failed_login_attempts
                )
            
            await self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(
                "Failed to increment failed login attempts",
                user_id=str(user_id),
                error=str(e)
            )
            return False
    
    def _generate_token(self, length: int = 32) -> str:
        """Generate secure random token"""
        return secrets.token_urlsafe(length)
    
    def _hash_token(self, token: str) -> str:
        """Hash token for secure storage"""
        return hashlib.sha256(token.encode()).hexdigest()