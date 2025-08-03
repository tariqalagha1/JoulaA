"""Organization service for Joulaa platform"""

import asyncio
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import selectinload

from ..models.organization import Organization, UserOrganization
from ..models.user import User
from ..schemas.organization import (
    OrganizationCreate, OrganizationUpdate, OrganizationResponse,
    OrganizationDetailResponse, OrganizationListResponse,
    OrganizationMemberCreate, OrganizationMemberUpdate,
    OrganizationMemberResponse, OrganizationStats
)
from ..core.exceptions import (
    OrganizationNotFoundError, OrganizationPermissionError,
    OrganizationValidationError, UserNotFoundError
)

logger = structlog.get_logger()


class OrganizationService:
    """Service for managing organizations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_organization(
        self,
        org_data: OrganizationCreate,
        created_by: UUID
    ) -> OrganizationResponse:
        """Create a new organization"""
        try:
            # Create organization instance
            organization = Organization(
                name_ar=org_data.name_ar,
                name_en=org_data.name_en,
                description_ar=org_data.description_ar,
                description_en=org_data.description_en,
                email=org_data.email,
                phone=org_data.phone,
                website=org_data.website,
                address_ar=org_data.address_ar,
                address_en=org_data.address_en,
                city=org_data.city,
                country=org_data.country,
                subscription_plan=org_data.subscription_plan,
                max_users=org_data.max_users,
                max_agents=org_data.max_agents,
                settings=org_data.settings or {},
                is_active=True
            )
            
            self.db.add(organization)
            await self.db.flush()  # Get the ID
            
            # Add creator as owner
            membership = UserOrganization(
                user_id=created_by,
                organization_id=organization.id,
                role="owner",
                is_active=True
            )
            
            self.db.add(membership)
            await self.db.commit()
            await self.db.refresh(organization)
            
            logger.info(
                "Organization created",
                organization_id=organization.id,
                name_ar=organization.name_ar,
                created_by=created_by
            )
            
            return OrganizationResponse(
                id=organization.id,
                name_ar=organization.name_ar,
                name_en=organization.name_en,
                description_ar=organization.description_ar,
                description_en=organization.description_en,
                email=organization.email,
                phone=organization.phone,
                website=organization.website,
                address_ar=organization.address_ar,
                address_en=organization.address_en,
                city=organization.city,
                country=organization.country,
                subscription_plan=organization.subscription_plan,
                max_users=organization.max_users,
                max_agents=organization.max_agents,
                is_active=organization.is_active,
                created_at=organization.created_at,
                updated_at=organization.updated_at
            )
            
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Organization creation failed",
                name_ar=org_data.name_ar,
                created_by=created_by,
                error=str(e),
                exc_info=True
            )
            raise
    
    async def get_organization(
        self,
        organization_id: UUID,
        requesting_user_id: UUID
    ) -> OrganizationDetailResponse:
        """Get organization by ID with detailed information"""
        try:
            # Check if user has access to this organization
            await self._check_organization_access(organization_id, requesting_user_id)
            
            query = select(Organization).where(Organization.id == organization_id)
            result = await self.db.execute(query)
            organization = result.scalar_one_or_none()
            
            if not organization:
                raise OrganizationNotFoundError(f"Organization with ID {organization_id} not found")
            
            # Get member count
            member_count_query = select(func.count(UserOrganization.user_id)).where(
                and_(
                    UserOrganization.organization_id == organization_id,
                    UserOrganization.is_active == True
                )
            )
            member_count_result = await self.db.execute(member_count_query)
            member_count = member_count_result.scalar() or 0
            
            # Get agent count (would need to implement when agent model is ready)
            agent_count = 0
            
            # Get members
            members_query = select(UserOrganization).options(
                selectinload(UserOrganization.user)
            ).where(
                and_(
                    UserOrganization.organization_id == organization_id,
                    UserOrganization.is_active == True
                )
            )
            members_result = await self.db.execute(members_query)
            memberships = members_result.scalars().all()
            
            members = []
            for membership in memberships:
                if membership.user:
                    members.append({
                        "user_id": membership.user_id,
                        "role": membership.role,
                        "joined_at": membership.joined_at,
                        "user": {
                            "id": membership.user.id,
                            "email": membership.user.email,
                            "username": membership.user.username,
                            "full_name_ar": membership.user.full_name_ar,
                            "full_name_en": membership.user.full_name_en
                        }
                    })
            
            return OrganizationDetailResponse(
                id=organization.id,
                name_ar=organization.name_ar,
                name_en=organization.name_en,
                description_ar=organization.description_ar,
                description_en=organization.description_en,
                email=organization.email,
                phone=organization.phone,
                website=organization.website,
                address_ar=organization.address_ar,
                address_en=organization.address_en,
                city=organization.city,
                country=organization.country,
                subscription_plan=organization.subscription_plan,
                max_users=organization.max_users,
                max_agents=organization.max_agents,
                is_active=organization.is_active,
                created_at=organization.created_at,
                updated_at=organization.updated_at,
                settings=organization.settings,
                member_count=member_count,
                agent_count=agent_count,
                members=members
            )
            
        except Exception as e:
            logger.error(
                "Failed to get organization",
                organization_id=organization_id,
                requesting_user_id=requesting_user_id,
                error=str(e)
            )
            raise
    
    async def list_organizations(
        self,
        requesting_user_id: UUID,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        subscription_plan: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> OrganizationListResponse:
        """List organizations with filtering and pagination"""
        try:
            # Build base query - only show organizations user is member of
            query = select(Organization).join(
                UserOrganization,
                Organization.id == UserOrganization.organization_id
            ).where(
                and_(
                    UserOrganization.user_id == requesting_user_id,
                    UserOrganization.is_active == True
                )
            )
            
            # Apply filters
            if search:
                search_filter = or_(
                    Organization.name_ar.ilike(f"%{search}%"),
                    Organization.name_en.ilike(f"%{search}%"),
                    Organization.description_ar.ilike(f"%{search}%"),
                    Organization.description_en.ilike(f"%{search}%")
                )
                query = query.where(search_filter)
            
            if is_active is not None:
                query = query.where(Organization.is_active == is_active)
            
            if subscription_plan:
                query = query.where(Organization.subscription_plan == subscription_plan)
            
            # Get total count
            count_query = select(func.count(Organization.id)).select_from(
                query.subquery()
            )
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()
            
            # Apply pagination
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)
            
            # Execute query
            result = await self.db.execute(query)
            organizations = result.scalars().all()
            
            # Convert to response format
            org_responses = [
                OrganizationResponse(
                    id=org.id,
                    name_ar=org.name_ar,
                    name_en=org.name_en,
                    description_ar=org.description_ar,
                    description_en=org.description_en,
                    email=org.email,
                    phone=org.phone,
                    website=org.website,
                    address_ar=org.address_ar,
                    address_en=org.address_en,
                    city=org.city,
                    country=org.country,
                    subscription_plan=org.subscription_plan,
                    max_users=org.max_users,
                    max_agents=org.max_agents,
                    is_active=org.is_active,
                    created_at=org.created_at,
                    updated_at=org.updated_at
                )
                for org in organizations
            ]
            
            return OrganizationListResponse(
                organizations=org_responses,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=(total + page_size - 1) // page_size
            )
            
        except Exception as e:
            logger.error(
                "Failed to list organizations",
                requesting_user_id=requesting_user_id,
                error=str(e)
            )
            raise
    
    async def update_organization(
        self,
        organization_id: UUID,
        org_data: OrganizationUpdate,
        requesting_user_id: UUID
    ) -> OrganizationResponse:
        """Update organization information"""
        try:
            # Check permissions
            await self._check_organization_permissions(
                organization_id, requesting_user_id, "update"
            )
            
            # Get existing organization
            query = select(Organization).where(Organization.id == organization_id)
            result = await self.db.execute(query)
            organization = result.scalar_one_or_none()
            
            if not organization:
                raise OrganizationNotFoundError(f"Organization with ID {organization_id} not found")
            
            # Update fields
            update_data = {}
            if org_data.name_ar is not None:
                update_data["name_ar"] = org_data.name_ar
            if org_data.name_en is not None:
                update_data["name_en"] = org_data.name_en
            if org_data.description_ar is not None:
                update_data["description_ar"] = org_data.description_ar
            if org_data.description_en is not None:
                update_data["description_en"] = org_data.description_en
            if org_data.email is not None:
                update_data["email"] = org_data.email
            if org_data.phone is not None:
                update_data["phone"] = org_data.phone
            if org_data.website is not None:
                update_data["website"] = org_data.website
            if org_data.address_ar is not None:
                update_data["address_ar"] = org_data.address_ar
            if org_data.address_en is not None:
                update_data["address_en"] = org_data.address_en
            if org_data.city is not None:
                update_data["city"] = org_data.city
            if org_data.country is not None:
                update_data["country"] = org_data.country
            if org_data.subscription_plan is not None:
                update_data["subscription_plan"] = org_data.subscription_plan
            if org_data.max_users is not None:
                update_data["max_users"] = org_data.max_users
            if org_data.max_agents is not None:
                update_data["max_agents"] = org_data.max_agents
            if org_data.is_active is not None:
                update_data["is_active"] = org_data.is_active
            if org_data.settings is not None:
                update_data["settings"] = org_data.settings
            
            if update_data:
                update_data["updated_at"] = datetime.utcnow()
                
                update_query = update(Organization).where(
                    Organization.id == organization_id
                ).values(**update_data)
                
                await self.db.execute(update_query)
                await self.db.commit()
                
                # Refresh organization data
                await self.db.refresh(organization)
            
            logger.info(
                "Organization updated",
                organization_id=organization_id,
                updated_by=requesting_user_id,
                fields=list(update_data.keys())
            )
            
            return OrganizationResponse(
                id=organization.id,
                name_ar=organization.name_ar,
                name_en=organization.name_en,
                description_ar=organization.description_ar,
                description_en=organization.description_en,
                email=organization.email,
                phone=organization.phone,
                website=organization.website,
                address_ar=organization.address_ar,
                address_en=organization.address_en,
                city=organization.city,
                country=organization.country,
                subscription_plan=organization.subscription_plan,
                max_users=organization.max_users,
                max_agents=organization.max_agents,
                is_active=organization.is_active,
                created_at=organization.created_at,
                updated_at=organization.updated_at
            )
            
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Organization update failed",
                organization_id=organization_id,
                requesting_user_id=requesting_user_id,
                error=str(e)
            )
            raise
    
    async def delete_organization(
        self,
        organization_id: UUID,
        requesting_user_id: UUID,
        soft_delete: bool = True
    ) -> bool:
        """Delete organization (soft delete by default)"""
        try:
            # Check permissions (only owner can delete)
            await self._check_organization_permissions(
                organization_id, requesting_user_id, "delete"
            )
            
            if soft_delete:
                # Soft delete - deactivate organization
                update_query = update(Organization).where(
                    Organization.id == organization_id
                ).values(
                    is_active=False,
                    updated_at=datetime.utcnow()
                )
                await self.db.execute(update_query)
            else:
                # Hard delete - remove organization and all memberships
                # First delete memberships
                delete_memberships = delete(UserOrganization).where(
                    UserOrganization.organization_id == organization_id
                )
                await self.db.execute(delete_memberships)
                
                # Then delete organization
                delete_org = delete(Organization).where(
                    Organization.id == organization_id
                )
                await self.db.execute(delete_org)
            
            await self.db.commit()
            
            logger.info(
                "Organization deleted",
                organization_id=organization_id,
                deleted_by=requesting_user_id,
                soft_delete=soft_delete
            )
            
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Organization deletion failed",
                organization_id=organization_id,
                requesting_user_id=requesting_user_id,
                error=str(e)
            )
            raise
    
    async def add_member(
        self,
        organization_id: UUID,
        member_data: OrganizationMemberCreate,
        requesting_user_id: UUID
    ) -> OrganizationMemberResponse:
        """Add member to organization"""
        try:
            # Check permissions
            await self._check_organization_permissions(
                organization_id, requesting_user_id, "manage_members"
            )
            
            # Check if user exists
            user_query = select(User).where(User.id == member_data.user_id)
            user_result = await self.db.execute(user_query)
            user = user_result.scalar_one_or_none()
            
            if not user:
                raise UserNotFoundError(f"User with ID {member_data.user_id} not found")
            
            # Check if user is already a member
            existing_query = select(UserOrganization).where(
                and_(
                    UserOrganization.user_id == member_data.user_id,
                    UserOrganization.organization_id == organization_id
                )
            )
            existing_result = await self.db.execute(existing_query)
            existing_membership = existing_result.scalar_one_or_none()
            
            if existing_membership:
                if existing_membership.is_active:
                    raise OrganizationValidationError("User is already a member of this organization")
                else:
                    # Reactivate existing membership
                    update_query = update(UserOrganization).where(
                        and_(
                            UserOrganization.user_id == member_data.user_id,
                            UserOrganization.organization_id == organization_id
                        )
                    ).values(
                        role=member_data.role,
                        is_active=True,
                        joined_at=datetime.utcnow()
                    )
                    await self.db.execute(update_query)
                    await self.db.commit()
                    
                    return OrganizationMemberResponse(
                        user_id=member_data.user_id,
                        organization_id=organization_id,
                        role=member_data.role,
                        is_active=True,
                        joined_at=datetime.utcnow()
                    )
            
            # Create new membership
            membership = UserOrganization(
                user_id=member_data.user_id,
                organization_id=organization_id,
                role=member_data.role,
                is_active=True
            )
            
            self.db.add(membership)
            await self.db.commit()
            await self.db.refresh(membership)
            
            logger.info(
                "Member added to organization",
                organization_id=organization_id,
                user_id=member_data.user_id,
                role=member_data.role,
                added_by=requesting_user_id
            )
            
            return OrganizationMemberResponse(
                user_id=membership.user_id,
                organization_id=membership.organization_id,
                role=membership.role,
                is_active=membership.is_active,
                joined_at=membership.joined_at
            )
            
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Failed to add member to organization",
                organization_id=organization_id,
                user_id=member_data.user_id,
                requesting_user_id=requesting_user_id,
                error=str(e)
            )
            raise
    
    async def remove_member(
        self,
        organization_id: UUID,
        user_id: UUID,
        requesting_user_id: UUID
    ) -> bool:
        """Remove member from organization"""
        try:
            # Check permissions
            await self._check_organization_permissions(
                organization_id, requesting_user_id, "manage_members"
            )
            
            # Cannot remove the owner
            owner_query = select(UserOrganization).where(
                and_(
                    UserOrganization.organization_id == organization_id,
                    UserOrganization.user_id == user_id,
                    UserOrganization.role == "owner"
                )
            )
            owner_result = await self.db.execute(owner_query)
            if owner_result.scalar_one_or_none():
                raise OrganizationValidationError("Cannot remove organization owner")
            
            # Soft delete - deactivate membership
            update_query = update(UserOrganization).where(
                and_(
                    UserOrganization.user_id == user_id,
                    UserOrganization.organization_id == organization_id
                )
            ).values(is_active=False)
            
            result = await self.db.execute(update_query)
            await self.db.commit()
            
            if result.rowcount == 0:
                raise OrganizationValidationError("User is not a member of this organization")
            
            logger.info(
                "Member removed from organization",
                organization_id=organization_id,
                user_id=user_id,
                removed_by=requesting_user_id
            )
            
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Failed to remove member from organization",
                organization_id=organization_id,
                user_id=user_id,
                requesting_user_id=requesting_user_id,
                error=str(e)
            )
            raise
    
    # Private helper methods
    
    async def _check_organization_access(
        self,
        organization_id: UUID,
        user_id: UUID
    ) -> None:
        """Check if user has access to organization"""
        query = select(UserOrganization).where(
            and_(
                UserOrganization.organization_id == organization_id,
                UserOrganization.user_id == user_id,
                UserOrganization.is_active == True
            )
        )
        result = await self.db.execute(query)
        membership = result.scalar_one_or_none()
        
        if not membership:
            raise OrganizationPermissionError("Access denied to organization")
    
    async def _check_organization_permissions(
        self,
        organization_id: UUID,
        user_id: UUID,
        action: str
    ) -> None:
        """Check if user has permission to perform action on organization"""
        query = select(UserOrganization).where(
            and_(
                UserOrganization.organization_id == organization_id,
                UserOrganization.user_id == user_id,
                UserOrganization.is_active == True
            )
        )
        result = await self.db.execute(query)
        membership = result.scalar_one_or_none()
        
        if not membership:
            raise OrganizationPermissionError("Access denied to organization")
        
        # Define permission levels
        permissions = {
            "owner": ["read", "update", "delete", "manage_members", "manage_settings"],
            "admin": ["read", "update", "manage_members"],
            "member": ["read"],
            "viewer": ["read"]
        }
        
        user_permissions = permissions.get(membership.role, [])
        
        if action not in user_permissions:
            raise OrganizationPermissionError(
                f"Insufficient permissions to {action} organization"
            )


# Custom exceptions
class OrganizationNotFoundError(Exception):
    pass

class OrganizationPermissionError(Exception):
    pass

class OrganizationValidationError(Exception):
    pass