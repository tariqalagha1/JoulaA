from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
import uuid
import asyncio
import aiohttp
import structlog

from ..models.integration import Integration
from ..models.organization import Organization
from ..schemas.integration import (
    IntegrationCreate, IntegrationUpdate, IntegrationSearchRequest,
    SyncStatus, HealthStatus, IntegrationType
)
from ..core.exceptions import (
    NotFoundError, ValidationError, PermissionError, 
    ConflictError, ExternalServiceError
)

logger = structlog.get_logger()


class IntegrationService:
    """Service for managing integrations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_integration(
        self, 
        integration_data: IntegrationCreate, 
        current_user_id: uuid.UUID
    ) -> Integration:
        """Create a new integration"""
        try:
            # Verify organization exists and user has access
            await self._check_organization_access(
                integration_data.organization_id, 
                current_user_id
            )
            
            # Check for duplicate integration names within organization
            existing = await self.db.execute(
                select(Integration).where(
                    and_(
                        Integration.organization_id == integration_data.organization_id,
                        Integration.name == integration_data.name,
                        Integration.is_deleted == False
                    )
                )
            )
            if existing.scalar_one_or_none():
                raise ConflictError(f"Integration with name '{integration_data.name}' already exists")
            
            # Validate configuration based on integration type
            await self._validate_integration_config(
                integration_data.integration_type, 
                integration_data.configuration
            )
            
            # Create integration
            integration = Integration(
                organization_id=integration_data.organization_id,
                integration_type=integration_data.integration_type,
                name=integration_data.name,
                description=integration_data.description,
                configuration=integration_data.configuration,
                is_active=integration_data.is_active,
                health_check_url=integration_data.health_check_url,
                metadata_=integration_data.metadata_,
                sync_status=SyncStatus.PENDING,
                health_status=HealthStatus.UNKNOWN,
                created_by=current_user_id,
                updated_by=current_user_id
            )
            
            self.db.add(integration)
            await self.db.commit()
            await self.db.refresh(integration)
            
            logger.info(
                "Integration created",
                integration_id=str(integration.id),
                name=integration.name,
                type=integration.integration_type,
                organization_id=str(integration.organization_id),
                created_by=str(current_user_id)
            )
            
            return integration
            
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Failed to create integration",
                error=str(e),
                integration_data=integration_data.dict(),
                user_id=str(current_user_id)
            )
            raise
    
    async def get_integration(
        self, 
        integration_id: uuid.UUID, 
        current_user_id: uuid.UUID,
        include_organization: bool = False
    ) -> Integration:
        """Get integration by ID"""
        query = select(Integration).where(
            and_(
                Integration.id == integration_id,
                Integration.is_deleted == False
            )
        )
        
        if include_organization:
            query = query.options(selectinload(Integration.organization))
        
        result = await self.db.execute(query)
        integration = result.scalar_one_or_none()
        
        if not integration:
            raise NotFoundError(f"Integration with ID {integration_id} not found")
        
        # Check access permissions
        await self._check_integration_access(integration, current_user_id)
        
        return integration
    
    async def list_integrations(
        self,
        search_params: IntegrationSearchRequest,
        current_user_id: uuid.UUID
    ) -> Tuple[List[Integration], int]:
        """List integrations with filtering and pagination"""
        # Get user's accessible organizations
        accessible_orgs = await self._get_user_organizations(current_user_id)
        
        # Build base query
        query = select(Integration).where(
            and_(
                Integration.organization_id.in_(accessible_orgs),
                Integration.is_deleted == False
            )
        )
        
        # Apply filters
        if search_params.query:
            search_term = f"%{search_params.query}%"
            query = query.where(
                or_(
                    Integration.name.ilike(search_term),
                    Integration.description.ilike(search_term)
                )
            )
        
        if search_params.integration_type:
            query = query.where(Integration.integration_type == search_params.integration_type)
        
        if search_params.is_active is not None:
            query = query.where(Integration.is_active == search_params.is_active)
        
        if search_params.health_status:
            query = query.where(Integration.health_status == search_params.health_status)
        
        if search_params.sync_status:
            query = query.where(Integration.sync_status == search_params.sync_status)
        
        if search_params.organization_id:
            if search_params.organization_id not in accessible_orgs:
                raise PermissionError("Access denied to specified organization")
            query = query.where(Integration.organization_id == search_params.organization_id)
        
        if search_params.created_after:
            query = query.where(Integration.created_at >= search_params.created_after)
        
        if search_params.created_before:
            query = query.where(Integration.created_at <= search_params.created_before)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply sorting
        if hasattr(Integration, search_params.sort_by):
            sort_field = getattr(Integration, search_params.sort_by)
            if search_params.sort_order == "desc":
                query = query.order_by(sort_field.desc())
            else:
                query = query.order_by(sort_field.asc())
        
        # Apply pagination
        offset = (search_params.page - 1) * search_params.page_size
        query = query.offset(offset).limit(search_params.page_size)
        
        # Execute query
        result = await self.db.execute(query)
        integrations = result.scalars().all()
        
        return list(integrations), total
    
    async def update_integration(
        self,
        integration_id: uuid.UUID,
        update_data: IntegrationUpdate,
        current_user_id: uuid.UUID
    ) -> Integration:
        """Update integration"""
        try:
            integration = await self.get_integration(integration_id, current_user_id)
            
            # Check for name conflicts if name is being updated
            if update_data.name and update_data.name != integration.name:
                existing = await self.db.execute(
                    select(Integration).where(
                        and_(
                            Integration.organization_id == integration.organization_id,
                            Integration.name == update_data.name,
                            Integration.id != integration_id,
                            Integration.is_deleted == False
                        )
                    )
                )
                if existing.scalar_one_or_none():
                    raise ConflictError(f"Integration with name '{update_data.name}' already exists")
            
            # Validate configuration if being updated
            if update_data.configuration is not None:
                await self._validate_integration_config(
                    integration.integration_type,
                    update_data.configuration
                )
            
            # Update fields
            update_dict = update_data.dict(exclude_unset=True, by_alias=True)
            for field, value in update_dict.items():
                if hasattr(integration, field):
                    setattr(integration, field, value)
            
            integration.updated_by = current_user_id
            
            await self.db.commit()
            await self.db.refresh(integration)
            
            logger.info(
                "Integration updated",
                integration_id=str(integration.id),
                updated_fields=list(update_dict.keys()),
                updated_by=str(current_user_id)
            )
            
            return integration
            
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Failed to update integration",
                integration_id=str(integration_id),
                error=str(e),
                user_id=str(current_user_id)
            )
            raise
    
    async def delete_integration(
        self,
        integration_id: uuid.UUID,
        current_user_id: uuid.UUID,
        soft_delete: bool = True
    ) -> bool:
        """Delete integration (soft delete by default)"""
        try:
            integration = await self.get_integration(integration_id, current_user_id)
            
            if soft_delete:
                integration.is_deleted = True
                integration.deleted_at = datetime.utcnow()
                integration.updated_by = current_user_id
                await self.db.commit()
            else:
                await self.db.delete(integration)
                await self.db.commit()
            
            logger.info(
                "Integration deleted",
                integration_id=str(integration_id),
                soft_delete=soft_delete,
                deleted_by=str(current_user_id)
            )
            
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Failed to delete integration",
                integration_id=str(integration_id),
                error=str(e),
                user_id=str(current_user_id)
            )
            raise
    
    async def sync_integration(
        self,
        integration_id: uuid.UUID,
        current_user_id: uuid.UUID,
        force: bool = False
    ) -> Dict[str, Any]:
        """Trigger integration synchronization"""
        try:
            integration = await self.get_integration(integration_id, current_user_id)
            
            if not integration.is_active:
                raise ValidationError("Cannot sync inactive integration")
            
            # Check if sync is needed (unless forced)
            if not force and not integration.needs_sync:
                return {
                    "integration_id": str(integration.id),
                    "sync_started": False,
                    "message": "Integration does not need synchronization",
                    "last_sync_at": integration.last_sync_at
                }
            
            # Update sync status
            integration.sync_status = SyncStatus.SYNCING
            integration.sync_error = None
            await self.db.commit()
            
            # Perform actual sync based on integration type
            sync_result = await self._perform_sync(integration)
            
            # Update sync results
            integration.sync_status = SyncStatus.SUCCESS if sync_result["success"] else SyncStatus.ERROR
            integration.last_sync_at = datetime.utcnow()
            if not sync_result["success"]:
                integration.sync_error = sync_result.get("error", "Unknown sync error")
            
            await self.db.commit()
            
            logger.info(
                "Integration sync completed",
                integration_id=str(integration.id),
                success=sync_result["success"],
                triggered_by=str(current_user_id)
            )
            
            return {
                "integration_id": str(integration.id),
                "sync_started": True,
                "sync_status": integration.sync_status,
                "message": sync_result.get("message", "Sync completed"),
                "details": sync_result.get("details")
            }
            
        except Exception as e:
            # Update sync status to error
            try:
                integration = await self.get_integration(integration_id, current_user_id)
                integration.sync_status = SyncStatus.ERROR
                integration.sync_error = str(e)
                await self.db.commit()
            except:
                pass
            
            logger.error(
                "Integration sync failed",
                integration_id=str(integration_id),
                error=str(e),
                user_id=str(current_user_id)
            )
            raise
    
    async def health_check_integration(
        self,
        integration_id: uuid.UUID,
        current_user_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Perform health check on integration"""
        try:
            integration = await self.get_integration(integration_id, current_user_id)
            
            if not integration.is_active:
                return {
                    "integration_id": str(integration.id),
                    "health_status": HealthStatus.UNHEALTHY,
                    "message": "Integration is inactive",
                    "checked_at": datetime.utcnow()
                }
            
            # Perform health check
            health_result = await self._perform_health_check(integration)
            
            # Update health status
            integration.health_status = health_result["status"]
            integration.last_health_check = datetime.utcnow()
            await self.db.commit()
            
            return {
                "integration_id": str(integration.id),
                "health_status": health_result["status"],
                "response_time": health_result.get("response_time"),
                "message": health_result.get("message", "Health check completed"),
                "details": health_result.get("details"),
                "checked_at": integration.last_health_check
            }
            
        except Exception as e:
            logger.error(
                "Health check failed",
                integration_id=str(integration_id),
                error=str(e),
                user_id=str(current_user_id)
            )
            raise
    
    async def get_integration_stats(
        self,
        organization_id: Optional[uuid.UUID],
        current_user_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Get integration statistics"""
        # Get accessible organizations
        accessible_orgs = await self._get_user_organizations(current_user_id)
        
        if organization_id:
            if organization_id not in accessible_orgs:
                raise PermissionError("Access denied to specified organization")
            org_filter = [organization_id]
        else:
            org_filter = accessible_orgs
        
        # Get basic counts
        base_query = select(Integration).where(
            and_(
                Integration.organization_id.in_(org_filter),
                Integration.is_deleted == False
            )
        )
        
        total_result = await self.db.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total = total_result.scalar()
        
        active_result = await self.db.execute(
            select(func.count()).select_from(
                base_query.where(Integration.is_active == True).subquery()
            )
        )
        active = active_result.scalar()
        
        healthy_result = await self.db.execute(
            select(func.count()).select_from(
                base_query.where(Integration.health_status == HealthStatus.HEALTHY).subquery()
            )
        )
        healthy = healthy_result.scalar()
        
        # Get integrations by type
        type_result = await self.db.execute(
            select(
                Integration.integration_type,
                func.count(Integration.id)
            ).where(
                and_(
                    Integration.organization_id.in_(org_filter),
                    Integration.is_deleted == False
                )
            ).group_by(Integration.integration_type)
        )
        
        integrations_by_type = {row[0]: row[1] for row in type_result.fetchall()}
        
        # Get recent sync errors
        recent_errors_result = await self.db.execute(
            select(func.count()).where(
                and_(
                    Integration.organization_id.in_(org_filter),
                    Integration.is_deleted == False,
                    Integration.sync_status == SyncStatus.ERROR,
                    Integration.last_sync_at >= datetime.utcnow() - timedelta(hours=24)
                )
            )
        )
        recent_errors = recent_errors_result.scalar()
        
        return {
            "total_integrations": total,
            "active_integrations": active,
            "inactive_integrations": total - active,
            "healthy_integrations": healthy,
            "unhealthy_integrations": total - healthy,
            "integrations_by_type": integrations_by_type,
            "recent_sync_errors": recent_errors,
            "last_updated": datetime.utcnow()
        }
    
    # Private helper methods
    
    async def _check_organization_access(
        self, 
        organization_id: uuid.UUID, 
        user_id: uuid.UUID
    ) -> None:
        """Check if user has access to organization"""
        from ..models.organization import UserOrganization
        
        result = await self.db.execute(
            select(UserOrganization).where(
                and_(
                    UserOrganization.user_id == user_id,
                    UserOrganization.organization_id == organization_id,
                    UserOrganization.is_active == True
                )
            )
        )
        
        if not result.scalar_one_or_none():
            raise PermissionError("Access denied to organization")
    
    async def _check_integration_access(
        self, 
        integration: Integration, 
        user_id: uuid.UUID
    ) -> None:
        """Check if user has access to integration"""
        await self._check_organization_access(integration.organization_id, user_id)
    
    async def _get_user_organizations(self, user_id: uuid.UUID) -> List[uuid.UUID]:
        """Get list of organization IDs user has access to"""
        from ..models.organization import UserOrganization
        
        result = await self.db.execute(
            select(UserOrganization.organization_id).where(
                and_(
                    UserOrganization.user_id == user_id,
                    UserOrganization.is_active == True
                )
            )
        )
        
        return [row[0] for row in result.fetchall()]
    
    async def _validate_integration_config(
        self, 
        integration_type: IntegrationType, 
        configuration: Dict[str, Any]
    ) -> None:
        """Validate integration configuration based on type"""
        # Basic validation - can be extended for specific integration types
        if not isinstance(configuration, dict):
            raise ValidationError("Configuration must be a dictionary")
        
        # Type-specific validation
        if integration_type == IntegrationType.SAP:
            required_fields = ["host", "client", "username"]
            for field in required_fields:
                if field not in configuration:
                    raise ValidationError(f"SAP integration requires '{field}' in configuration")
        
        elif integration_type == IntegrationType.ORACLE:
            required_fields = ["host", "port", "service_name", "username"]
            for field in required_fields:
                if field not in configuration:
                    raise ValidationError(f"Oracle integration requires '{field}' in configuration")
        
        elif integration_type == IntegrationType.API:
            if "base_url" not in configuration:
                raise ValidationError("API integration requires 'base_url' in configuration")
    
    async def _perform_sync(self, integration: Integration) -> Dict[str, Any]:
        """Perform actual synchronization based on integration type"""
        try:
            # This is a placeholder - implement actual sync logic based on integration type
            if integration.integration_type == IntegrationType.SAP:
                return await self._sync_sap_integration(integration)
            elif integration.integration_type == IntegrationType.ORACLE:
                return await self._sync_oracle_integration(integration)
            elif integration.integration_type == IntegrationType.API:
                return await self._sync_api_integration(integration)
            else:
                return {
                    "success": True,
                    "message": f"Sync completed for {integration.integration_type} integration",
                    "details": {"records_synced": 0}
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Sync failed for {integration.integration_type} integration"
            }
    
    async def _perform_health_check(self, integration: Integration) -> Dict[str, Any]:
        """Perform health check on integration"""
        try:
            start_time = datetime.utcnow()
            
            if integration.health_check_url:
                # Perform HTTP health check
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        integration.health_check_url,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                        
                        if response.status == 200:
                            return {
                                "status": HealthStatus.HEALTHY,
                                "response_time": response_time,
                                "message": "Health check passed"
                            }
                        else:
                            return {
                                "status": HealthStatus.UNHEALTHY,
                                "response_time": response_time,
                                "message": f"Health check failed with status {response.status}"
                            }
            else:
                # Basic configuration check
                if integration.configuration and integration.is_active:
                    return {
                        "status": HealthStatus.HEALTHY,
                        "message": "Integration configuration is valid"
                    }
                else:
                    return {
                        "status": HealthStatus.UNHEALTHY,
                        "message": "Integration configuration is invalid or inactive"
                    }
                    
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Health check failed: {str(e)}"
            }
    
    # Placeholder sync methods for different integration types
    async def _sync_sap_integration(self, integration: Integration) -> Dict[str, Any]:
        """Sync SAP integration - placeholder implementation"""
        await asyncio.sleep(1)  # Simulate sync time
        return {
            "success": True,
            "message": "SAP integration synced successfully",
            "details": {"records_synced": 100}
        }
    
    async def _sync_oracle_integration(self, integration: Integration) -> Dict[str, Any]:
        """Sync Oracle integration - placeholder implementation"""
        await asyncio.sleep(1)  # Simulate sync time
        return {
            "success": True,
            "message": "Oracle integration synced successfully",
            "details": {"records_synced": 150}
        }
    
    async def _sync_api_integration(self, integration: Integration) -> Dict[str, Any]:
        """Sync API integration - placeholder implementation"""
        await asyncio.sleep(1)  # Simulate sync time
        return {
            "success": True,
            "message": "API integration synced successfully",
            "details": {"records_synced": 75}
        }