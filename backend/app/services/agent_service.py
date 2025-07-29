import asyncio
import json
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import selectinload

from ..models.agent import (
    AIAgent, AgentMetrics, AgentTemplate, AgentWorkflow,
    AgentType, AgentStatus, AgentCapability
)
from ..models.user import User
from ..schemas.agent import (
    AgentCreate, AgentUpdate, AgentResponse, AgentDetailResponse,
    AgentListResponse, AgentMetricsResponse, AgentTemplateResponse,
    AgentWorkflowResponse, BulkAgentOperation, BulkAgentOperationResponse
)
from ..core.feature_flags import is_feature_enabled, FeatureFlag
from ..core.exceptions import (
    AgentNotFoundError, AgentPermissionError, AgentValidationError,
    AgentLimitExceededError
)
from .ai_service import ai_service

logger = structlog.get_logger()


class AgentService:
    """Service for managing AI agents"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_agent(
        self,
        agent_data: AgentCreate,
        user_id: UUID,
        organization_id: UUID
    ) -> AgentResponse:
        """Create a new AI agent"""
        try:
            # Check agent creation limits
            await self._check_agent_limits(organization_id)
            
            # Validate agent configuration
            await self._validate_agent_config(agent_data)
            
            # Create agent instance
            agent = AIAgent(
                id=uuid4(),
                name=agent_data.name,
                description=agent_data.description,
                agent_type=agent_data.agent_type,
                capabilities=agent_data.capabilities or [],
                llm_provider=agent_data.llm_provider or "openai",
                llm_model=agent_data.llm_model,
                system_prompt_ar=agent_data.system_prompt_ar,
                system_prompt_en=agent_data.system_prompt_en,
                temperature=agent_data.temperature or 0.7,
                max_tokens=agent_data.max_tokens or 4000,
                configuration=agent_data.configuration or {},
                integrations=agent_data.integrations or {},
                permissions=agent_data.permissions or {},
                is_active=True,
                status=AgentStatus.ACTIVE,
                created_by=user_id,
                organization_id=organization_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(agent)
            await self.db.commit()
            await self.db.refresh(agent)
            
            # Create initial metrics
            await self._create_agent_metrics(agent.id)
            
            logger.info(
                "Agent created successfully",
                agent_id=agent.id,
                agent_name=agent.name,
                agent_type=agent.agent_type.value,
                created_by=user_id,
                organization_id=organization_id
            )
            
            return AgentResponse.from_orm(agent)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Failed to create agent",
                error=str(e),
                agent_name=agent_data.name,
                user_id=user_id,
                organization_id=organization_id,
                exc_info=True
            )
            raise
    
    async def get_agent(
        self,
        agent_id: UUID,
        user_id: UUID,
        organization_id: UUID,
        include_metrics: bool = False
    ) -> AgentDetailResponse:
        """Get agent by ID with detailed information"""
        try:
            # Query agent with optional metrics
            query = select(AIAgent).where(
                and_(
                    AIAgent.id == agent_id,
                    AIAgent.organization_id == organization_id
                )
            )
            
            result = await self.db.execute(query)
            agent = result.scalar_one_or_none()
            
            if not agent:
                raise AgentNotFoundError(f"Agent {agent_id} not found")
            
            # Check permissions
            await self._check_agent_permissions(agent, user_id, "read")
            
            # Get metrics if requested
            metrics = None
            if include_metrics:
                metrics = await self._get_agent_metrics(agent_id)
            
            # Get recent conversations count
            recent_conversations = await self._get_recent_conversations_count(agent_id)
            
            response = AgentDetailResponse.from_orm(agent)
            if metrics:
                response.metrics = AgentMetricsResponse.from_orm(metrics)
            response.recent_conversations = recent_conversations
            
            return response
            
        except AgentNotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Failed to get agent",
                agent_id=agent_id,
                user_id=user_id,
                error=str(e),
                exc_info=True
            )
            raise
    
    async def list_agents(
        self,
        user_id: UUID,
        organization_id: UUID,
        agent_type: Optional[AgentType] = None,
        status: Optional[AgentStatus] = None,
        capabilities: Optional[List[AgentCapability]] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> AgentListResponse:
        """List agents with filtering and pagination"""
        try:
            # Build query
            query = select(AIAgent).where(
                AIAgent.organization_id == organization_id
            )
            
            # Apply filters
            if agent_type:
                query = query.where(AIAgent.agent_type == agent_type)
            
            if status:
                query = query.where(AIAgent.status == status)
            
            if capabilities:
                for capability in capabilities:
                    query = query.where(AIAgent.capabilities.contains([capability]))
            
            if search:
                search_filter = or_(
                    AIAgent.name.ilike(f"%{search}%"),
                    AIAgent.description.ilike(f"%{search}%")
                )
                query = query.where(search_filter)
            
            # Get total count
            count_query = select(func.count(AIAgent.id)).where(
                query.whereclause
            )
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()
            
            # Apply pagination
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)
            query = query.order_by(AIAgent.updated_at.desc())
            
            # Execute query
            result = await self.db.execute(query)
            agents = result.scalars().all()
            
            # Convert to response objects
            agent_responses = [AgentResponse.from_orm(agent) for agent in agents]
            
            return AgentListResponse(
                agents=agent_responses,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=(total + page_size - 1) // page_size
            )
            
        except Exception as e:
            logger.error(
                "Failed to list agents",
                user_id=user_id,
                organization_id=organization_id,
                error=str(e),
                exc_info=True
            )
            raise
    
    async def update_agent(
        self,
        agent_id: UUID,
        agent_data: AgentUpdate,
        user_id: UUID,
        organization_id: UUID
    ) -> AgentResponse:
        """Update an existing agent"""
        try:
            # Get existing agent
            query = select(AIAgent).where(
                and_(
                    AIAgent.id == agent_id,
                    AIAgent.organization_id == organization_id
                )
            )
            result = await self.db.execute(query)
            agent = result.scalar_one_or_none()
            
            if not agent:
                raise AgentNotFoundError(f"Agent {agent_id} not found")
            
            # Check permissions
            await self._check_agent_permissions(agent, user_id, "write")
            
            # Validate configuration if provided
            if agent_data.configuration is not None:
                await self._validate_agent_config(agent_data)
            
            # Update agent fields
            update_data = agent_data.dict(exclude_unset=True)
            update_data['updated_at'] = datetime.utcnow()
            
            for field, value in update_data.items():
                if hasattr(agent, field):
                    setattr(agent, field, value)
            
            await self.db.commit()
            await self.db.refresh(agent)
            
            logger.info(
                "Agent updated successfully",
                agent_id=agent_id,
                updated_by=user_id,
                updated_fields=list(update_data.keys())
            )
            
            return AgentResponse.from_orm(agent)
            
        except AgentNotFoundError:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Failed to update agent",
                agent_id=agent_id,
                user_id=user_id,
                error=str(e),
                exc_info=True
            )
            raise
    
    async def delete_agent(
        self,
        agent_id: UUID,
        user_id: UUID,
        organization_id: UUID,
        force: bool = False
    ) -> bool:
        """Delete an agent"""
        try:
            # Get existing agent
            query = select(AIAgent).where(
                and_(
                    AIAgent.id == agent_id,
                    AIAgent.organization_id == organization_id
                )
            )
            result = await self.db.execute(query)
            agent = result.scalar_one_or_none()
            
            if not agent:
                raise AgentNotFoundError(f"Agent {agent_id} not found")
            
            # Check permissions
            await self._check_agent_permissions(agent, user_id, "delete")
            
            # Check if agent has active conversations (unless force delete)
            if not force:
                active_conversations = await self._get_active_conversations_count(agent_id)
                if active_conversations > 0:
                    raise AgentValidationError(
                        f"Cannot delete agent with {active_conversations} active conversations. Use force=True to override."
                    )
            
            # Soft delete by default
            if is_feature_enabled(FeatureFlag.SOFT_DELETE):
                agent.is_active = False
                agent.status = AgentStatus.DELETED
                agent.updated_at = datetime.utcnow()
                await self.db.commit()
            else:
                # Hard delete
                await self.db.delete(agent)
                await self.db.commit()
            
            logger.info(
                "Agent deleted successfully",
                agent_id=agent_id,
                deleted_by=user_id,
                force_delete=force,
                soft_delete=is_feature_enabled(FeatureFlag.SOFT_DELETE)
            )
            
            return True
            
        except (AgentNotFoundError, AgentValidationError):
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Failed to delete agent",
                agent_id=agent_id,
                user_id=user_id,
                error=str(e),
                exc_info=True
            )
            raise
    
    async def bulk_operation(
        self,
        operation: BulkAgentOperation,
        user_id: UUID,
        organization_id: UUID
    ) -> BulkAgentOperationResponse:
        """Perform bulk operations on agents"""
        try:
            results = []
            errors = []
            
            for agent_id in operation.agent_ids:
                try:
                    if operation.operation == "activate":
                        await self._bulk_activate_agent(agent_id, user_id, organization_id)
                        results.append({"agent_id": agent_id, "status": "success"})
                    
                    elif operation.operation == "deactivate":
                        await self._bulk_deactivate_agent(agent_id, user_id, organization_id)
                        results.append({"agent_id": agent_id, "status": "success"})
                    
                    elif operation.operation == "delete":
                        await self.delete_agent(agent_id, user_id, organization_id, force=operation.force)
                        results.append({"agent_id": agent_id, "status": "success"})
                    
                    elif operation.operation == "update_config":
                        if operation.config_updates:
                            await self._bulk_update_config(agent_id, operation.config_updates, user_id, organization_id)
                            results.append({"agent_id": agent_id, "status": "success"})
                    
                except Exception as e:
                    errors.append({
                        "agent_id": agent_id,
                        "error": str(e)
                    })
            
            await self.db.commit()
            
            return BulkAgentOperationResponse(
                operation=operation.operation,
                total_agents=len(operation.agent_ids),
                successful=len(results),
                failed=len(errors),
                results=results,
                errors=errors
            )
            
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Bulk operation failed",
                operation=operation.operation,
                user_id=user_id,
                error=str(e),
                exc_info=True
            )
            raise
    
    async def get_agent_templates(
        self,
        organization_id: UUID,
        agent_type: Optional[AgentType] = None,
        language: str = "ar"
    ) -> List[AgentTemplateResponse]:
        """Get available agent templates"""
        try:
            query = select(AgentTemplate).where(
                or_(
                    AgentTemplate.organization_id == organization_id,
                    AgentTemplate.organization_id.is_(None)  # Global templates
                )
            )
            
            if agent_type:
                query = query.where(AgentTemplate.agent_type == agent_type)
            
            result = await self.db.execute(query)
            templates = result.scalars().all()
            
            return [AgentTemplateResponse.from_orm(template) for template in templates]
            
        except Exception as e:
            logger.error(
                "Failed to get agent templates",
                organization_id=organization_id,
                error=str(e),
                exc_info=True
            )
            raise
    
    async def create_agent_from_template(
        self,
        template_id: UUID,
        agent_name: str,
        user_id: UUID,
        organization_id: UUID,
        customizations: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Create an agent from a template"""
        try:
            # Get template
            query = select(AgentTemplate).where(AgentTemplate.id == template_id)
            result = await self.db.execute(query)
            template = result.scalar_one_or_none()
            
            if not template:
                raise AgentNotFoundError(f"Template {template_id} not found")
            
            # Create agent data from template
            agent_data = AgentCreate(
                name=agent_name,
                description=template.description,
                agent_type=template.agent_type,
                capabilities=template.capabilities,
                llm_provider=template.llm_provider,
                llm_model=template.llm_model,
                system_prompt_ar=template.system_prompt_ar,
                system_prompt_en=template.system_prompt_en,
                temperature=template.temperature,
                max_tokens=template.max_tokens,
                configuration=template.configuration.copy() if template.configuration else {},
                integrations=template.integrations.copy() if template.integrations else {},
                permissions=template.permissions.copy() if template.permissions else {}
            )
            
            # Apply customizations
            if customizations:
                for key, value in customizations.items():
                    if hasattr(agent_data, key):
                        setattr(agent_data, key, value)
            
            # Create agent
            return await self.create_agent(agent_data, user_id, organization_id)
            
        except AgentNotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Failed to create agent from template",
                template_id=template_id,
                user_id=user_id,
                error=str(e),
                exc_info=True
            )
            raise
    
    # Private helper methods
    
    async def _check_agent_limits(self, organization_id: UUID) -> None:
        """Check if organization has reached agent creation limits"""
        if not is_feature_enabled(FeatureFlag.AGENT_LIMITS):
            return
        
        # Get current agent count
        query = select(func.count(AIAgent.id)).where(
            and_(
                AIAgent.organization_id == organization_id,
                AIAgent.is_active == True
            )
        )
        result = await self.db.execute(query)
        current_count = result.scalar()
        
        # Check against limit (this would come from organization settings)
        max_agents = 50  # Default limit, should be configurable
        
        if current_count >= max_agents:
            raise AgentLimitExceededError(
                f"Organization has reached the maximum limit of {max_agents} agents"
            )
    
    async def _validate_agent_config(self, agent_data) -> None:
        """Validate agent configuration"""
        # Validate LLM provider
        supported_providers = ["openai", "anthropic"]
        if agent_data.llm_provider and agent_data.llm_provider not in supported_providers:
            raise AgentValidationError(f"Unsupported LLM provider: {agent_data.llm_provider}")
        
        # Validate temperature
        if agent_data.temperature is not None:
            if not 0.0 <= agent_data.temperature <= 2.0:
                raise AgentValidationError("Temperature must be between 0.0 and 2.0")
        
        # Validate max_tokens
        if agent_data.max_tokens is not None:
            if not 1 <= agent_data.max_tokens <= 32000:
                raise AgentValidationError("Max tokens must be between 1 and 32000")
    
    async def _check_agent_permissions(self, agent: AIAgent, user_id: UUID, action: str) -> None:
        """Check if user has permission to perform action on agent"""
        # For now, allow all actions for users in the same organization
        # In a real implementation, this would check RBAC permissions
        pass
    
    async def _create_agent_metrics(self, agent_id: UUID) -> None:
        """Create initial metrics for an agent"""
        metrics = AgentMetrics(
            id=uuid4(),
            agent_id=agent_id,
            total_conversations=0,
            total_messages=0,
            total_tokens_used=0,
            average_response_time=0.0,
            success_rate=1.0,
            user_satisfaction=0.0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(metrics)
    
    async def _get_agent_metrics(self, agent_id: UUID) -> Optional[AgentMetrics]:
        """Get agent metrics"""
        query = select(AgentMetrics).where(AgentMetrics.agent_id == agent_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def _get_recent_conversations_count(self, agent_id: UUID) -> int:
        """Get count of recent conversations for an agent"""
        # This would query the conversations table
        # For now, return 0 as placeholder
        return 0
    
    async def _get_active_conversations_count(self, agent_id: UUID) -> int:
        """Get count of active conversations for an agent"""
        # This would query the conversations table for active conversations
        # For now, return 0 as placeholder
        return 0
    
    async def _bulk_activate_agent(self, agent_id: UUID, user_id: UUID, organization_id: UUID) -> None:
        """Activate an agent in bulk operation"""
        query = update(AIAgent).where(
            and_(
                AIAgent.id == agent_id,
                AIAgent.organization_id == organization_id
            )
        ).values(
            is_active=True,
            status=AgentStatus.ACTIVE,
            updated_at=datetime.utcnow()
        )
        
        await self.db.execute(query)
    
    async def _bulk_deactivate_agent(self, agent_id: UUID, user_id: UUID, organization_id: UUID) -> None:
        """Deactivate an agent in bulk operation"""
        query = update(AIAgent).where(
            and_(
                AIAgent.id == agent_id,
                AIAgent.organization_id == organization_id
            )
        ).values(
            is_active=False,
            status=AgentStatus.INACTIVE,
            updated_at=datetime.utcnow()
        )
        
        await self.db.execute(query)
    
    async def _bulk_update_config(
        self,
        agent_id: UUID,
        config_updates: Dict[str, Any],
        user_id: UUID,
        organization_id: UUID
    ) -> None:
        """Update agent configuration in bulk operation"""
        # Get current agent
        query = select(AIAgent).where(
            and_(
                AIAgent.id == agent_id,
                AIAgent.organization_id == organization_id
            )
        )
        result = await self.db.execute(query)
        agent = result.scalar_one_or_none()
        
        if agent:
            # Update configuration
            current_config = agent.configuration or {}
            current_config.update(config_updates)
            
            update_query = update(AIAgent).where(
                AIAgent.id == agent_id
            ).values(
                configuration=current_config,
                updated_at=datetime.utcnow()
            )
            
            await self.db.execute(update_query)


# Custom exceptions
class AgentNotFoundError(Exception):
    pass

class AgentPermissionError(Exception):
    pass

class AgentValidationError(Exception):
    pass

class AgentLimitExceededError(Exception):
    pass