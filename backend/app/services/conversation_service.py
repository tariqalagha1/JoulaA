from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload, joinedload
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime, timedelta
import math

from ..models.conversation import Conversation, Message
from ..models.user import User
from ..models.agent import AIAgent
from ..schemas.conversation import (
    ConversationCreate, ConversationUpdate, ConversationResponse,
    ConversationDetailResponse, ConversationListResponse,
    MessageCreate, MessageUpdate, MessageResponse, MessageListResponse,
    ConversationSearchRequest, ConversationStats,
    BulkConversationOperation, BulkConversationOperationResponse
)
from ..core.exceptions import (
    ConversationNotFoundError, ConversationPermissionError,
    ConversationValidationError, MessageNotFoundError
)


class ConversationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_conversation(
        self,
        conversation_data: ConversationCreate,
        user_id: UUID
    ) -> ConversationResponse:
        """Create a new conversation"""
        try:
            # Validate agent exists if provided
            if conversation_data.agent_id:
                agent_query = select(AIAgent).where(AIAgent.id == conversation_data.agent_id)
                agent_result = await self.db.execute(agent_query)
                agent = agent_result.scalar_one_or_none()
                if not agent:
                    raise ConversationValidationError("Agent not found")
                if not agent.is_active:
                    raise ConversationValidationError("Agent is not active")

            # Create conversation
            conversation = Conversation(
                title=conversation_data.title,
                summary=conversation_data.summary,
                language=conversation_data.language,
                status=conversation_data.status,
                user_id=user_id,
                agent_id=conversation_data.agent_id,
                organization_id=conversation_data.organization_id,
                settings=conversation_data.settings,
                conversation_metadata=conversation_data.conversation_metadata,
                started_at=datetime.utcnow()
            )

            self.db.add(conversation)
            await self.db.flush()

            # Add initial message if provided
            if conversation_data.initial_message:
                initial_message = Message(
                    content=conversation_data.initial_message,
                    role="user",
                    message_type="text",
                    language=conversation_data.language,
                    conversation_id=conversation.id,
                    user_id=user_id
                )
                self.db.add(initial_message)
                conversation.message_count = 1
                conversation.last_message_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(conversation)

            return ConversationResponse.from_orm(conversation)

        except Exception as e:
            await self.db.rollback()
            if isinstance(e, (ConversationValidationError,)):
                raise
            raise ConversationValidationError(f"Failed to create conversation: {str(e)}")

    async def get_conversation(
        self,
        conversation_id: UUID,
        user_id: UUID,
        include_messages: bool = False,
        message_limit: int = 50
    ) -> ConversationDetailResponse:
        """Get conversation by ID"""
        query = select(Conversation).where(Conversation.id == conversation_id)
        
        if include_messages:
            query = query.options(
                selectinload(Conversation.messages).options(
                    joinedload(Message.user)
                ).limit(message_limit)
            )
        
        query = query.options(
            joinedload(Conversation.user),
            joinedload(Conversation.agent)
        )

        result = await self.db.execute(query)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise ConversationNotFoundError("Conversation not found")

        # Check permissions
        await self._check_conversation_access(conversation, user_id)

        # Convert to response
        response_data = {
            **conversation.__dict__,
            "display_title": conversation.display_title
        }
        
        if include_messages and conversation.messages:
            # Sort messages by creation time
            sorted_messages = sorted(conversation.messages, key=lambda m: m.created_at)
            response_data["messages"] = [MessageResponse.from_orm(msg) for msg in sorted_messages]
            response_data["recent_messages"] = [MessageResponse.from_orm(msg) for msg in sorted_messages[-10:]]
        else:
            response_data["messages"] = []
            response_data["recent_messages"] = []

        return ConversationDetailResponse(**response_data)

    async def list_conversations(
        self,
        user_id: UUID,
        search_request: ConversationSearchRequest
    ) -> ConversationListResponse:
        """List conversations with filtering and pagination"""
        query = select(Conversation).where(Conversation.user_id == user_id)

        # Apply filters
        if search_request.query:
            search_term = f"%{search_request.query}%"
            query = query.where(
                or_(
                    Conversation.title.ilike(search_term),
                    Conversation.summary.ilike(search_term)
                )
            )

        if search_request.agent_id:
            query = query.where(Conversation.agent_id == search_request.agent_id)

        if search_request.status:
            query = query.where(Conversation.status == search_request.status)

        if search_request.language:
            query = query.where(Conversation.language == search_request.language)

        if search_request.date_from:
            query = query.where(Conversation.created_at >= search_request.date_from)

        if search_request.date_to:
            query = query.where(Conversation.created_at <= search_request.date_to)

        if search_request.min_messages is not None:
            query = query.where(Conversation.message_count >= search_request.min_messages)

        if search_request.max_messages is not None:
            query = query.where(Conversation.message_count <= search_request.max_messages)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Apply sorting
        sort_column = getattr(Conversation, search_request.sort_by, Conversation.last_message_at)
        if search_request.sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Apply pagination
        offset = (search_request.page - 1) * search_request.page_size
        query = query.offset(offset).limit(search_request.page_size)

        # Load relationships
        query = query.options(
            joinedload(Conversation.user),
            joinedload(Conversation.agent)
        )

        result = await self.db.execute(query)
        conversations = result.scalars().all()

        # Convert to response
        conversation_responses = [
            ConversationResponse.from_orm(conv) for conv in conversations
        ]

        total_pages = math.ceil(total / search_request.page_size)

        return ConversationListResponse(
            conversations=conversation_responses,
            total=total,
            page=search_request.page,
            page_size=search_request.page_size,
            total_pages=total_pages
        )

    async def update_conversation(
        self,
        conversation_id: UUID,
        conversation_data: ConversationUpdate,
        user_id: UUID
    ) -> ConversationResponse:
        """Update conversation"""
        # Get conversation
        query = select(Conversation).where(Conversation.id == conversation_id)
        result = await self.db.execute(query)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise ConversationNotFoundError("Conversation not found")

        # Check permissions
        await self._check_conversation_access(conversation, user_id)

        # Update fields
        update_data = conversation_data.dict(exclude_unset=True)
        if update_data:
            for field, value in update_data.items():
                setattr(conversation, field, value)

            await self.db.commit()
            await self.db.refresh(conversation)

        return ConversationResponse.from_orm(conversation)

    async def delete_conversation(
        self,
        conversation_id: UUID,
        user_id: UUID,
        soft_delete: bool = True
    ) -> None:
        """Delete conversation"""
        # Get conversation
        query = select(Conversation).where(Conversation.id == conversation_id)
        result = await self.db.execute(query)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise ConversationNotFoundError("Conversation not found")

        # Check permissions
        await self._check_conversation_access(conversation, user_id)

        if soft_delete:
            conversation.status = "deleted"
            conversation.ended_at = datetime.utcnow()
            await self.db.commit()
        else:
            await self.db.delete(conversation)
            await self.db.commit()

    async def add_message(
        self,
        message_data: MessageCreate,
        user_id: UUID
    ) -> MessageResponse:
        """Add message to conversation"""
        # Get conversation
        if not message_data.conversation_id:
            raise ConversationValidationError("Conversation ID is required")

        query = select(Conversation).where(Conversation.id == message_data.conversation_id)
        result = await self.db.execute(query)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise ConversationNotFoundError("Conversation not found")

        # Check permissions
        await self._check_conversation_access(conversation, user_id)

        # Create message
        message = Message(
            content=message_data.content,
            role=message_data.role,
            message_type=message_data.message_type,
            language=message_data.language,
            conversation_id=message_data.conversation_id,
            user_id=user_id if message_data.role == "user" else None,
            attachments=message_data.attachments,
            message_metadata=message_data.message_metadata
        )

        self.db.add(message)

        # Update conversation
        conversation.message_count += 1
        conversation.last_message_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(message)

        return MessageResponse.from_orm(message)

    async def get_messages(
        self,
        conversation_id: UUID,
        user_id: UUID,
        page: int = 1,
        page_size: int = 50
    ) -> MessageListResponse:
        """Get messages for conversation"""
        # Check conversation access
        conv_query = select(Conversation).where(Conversation.id == conversation_id)
        conv_result = await self.db.execute(conv_query)
        conversation = conv_result.scalar_one_or_none()

        if not conversation:
            raise ConversationNotFoundError("Conversation not found")

        await self._check_conversation_access(conversation, user_id)

        # Get messages
        query = select(Message).where(Message.conversation_id == conversation_id)
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination and ordering
        offset = (page - 1) * page_size
        query = query.order_by(Message.created_at).offset(offset).limit(page_size)
        query = query.options(joinedload(Message.user))

        result = await self.db.execute(query)
        messages = result.scalars().all()

        # Convert to response
        message_responses = [MessageResponse.from_orm(msg) for msg in messages]
        total_pages = math.ceil(total / page_size)

        return MessageListResponse(
            messages=message_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    async def get_conversation_stats(
        self,
        user_id: UUID,
        days: int = 30
    ) -> ConversationStats:
        """Get conversation statistics for user"""
        date_from = datetime.utcnow() - timedelta(days=days)
        
        # Total conversations
        total_query = select(func.count()).where(Conversation.user_id == user_id)
        total_result = await self.db.execute(total_query)
        total_conversations = total_result.scalar()

        # Active conversations
        active_query = select(func.count()).where(
            and_(
                Conversation.user_id == user_id,
                Conversation.status == "active"
            )
        )
        active_result = await self.db.execute(active_query)
        active_conversations = active_result.scalar()

        # Archived conversations
        archived_query = select(func.count()).where(
            and_(
                Conversation.user_id == user_id,
                Conversation.status == "archived"
            )
        )
        archived_result = await self.db.execute(archived_query)
        archived_conversations = archived_result.scalar()

        # Total messages
        messages_query = select(func.sum(Conversation.message_count)).where(
            Conversation.user_id == user_id
        )
        messages_result = await self.db.execute(messages_query)
        total_messages = messages_result.scalar() or 0

        # Average messages per conversation
        avg_messages = total_messages / total_conversations if total_conversations > 0 else 0

        return ConversationStats(
            total_conversations=total_conversations,
            active_conversations=active_conversations,
            archived_conversations=archived_conversations,
            total_messages=total_messages,
            average_messages_per_conversation=avg_messages,
            most_used_agents=[],  # TODO: Implement
            conversation_languages={},  # TODO: Implement
            daily_conversation_count=[]  # TODO: Implement
        )

    async def _check_conversation_access(
        self,
        conversation: Conversation,
        user_id: UUID
    ) -> None:
        """Check if user has access to conversation"""
        if conversation.user_id != user_id:
            # Check if user is member of organization
            if conversation.organization_id:
                from ..models.organization import UserOrganization
                org_query = select(UserOrganization).where(
                    and_(
                        UserOrganization.user_id == user_id,
                        UserOrganization.organization_id == conversation.organization_id,
                        UserOrganization.is_active == True
                    )
                )
                org_result = await self.db.execute(org_query)
                membership = org_result.scalar_one_or_none()
                
                if not membership:
                    raise ConversationPermissionError("Access denied to conversation")
            else:
                raise ConversationPermissionError("Access denied to conversation")

    async def bulk_operation(
        self,
        operation_data: BulkConversationOperation,
        user_id: UUID
    ) -> BulkConversationOperationResponse:
        """Perform bulk operations on conversations"""
        successful = 0
        failed = 0
        errors = []
        results = []

        for conversation_id in operation_data.conversation_ids:
            try:
                if operation_data.operation == "archive":
                    await self.update_conversation(
                        conversation_id,
                        ConversationUpdate(status="archived"),
                        user_id
                    )
                elif operation_data.operation == "delete":
                    await self.delete_conversation(conversation_id, user_id, soft_delete=True)
                elif operation_data.operation == "restore":
                    await self.update_conversation(
                        conversation_id,
                        ConversationUpdate(status="active"),
                        user_id
                    )
                
                successful += 1
                results.append({"conversation_id": str(conversation_id), "status": "success"})
                
            except Exception as e:
                failed += 1
                errors.append({
                    "conversation_id": str(conversation_id),
                    "error": str(e)
                })
                results.append({"conversation_id": str(conversation_id), "status": "failed"})

        return BulkConversationOperationResponse(
            operation=operation_data.operation,
            total_requested=len(operation_data.conversation_ids),
            successful=successful,
            failed=failed,
            errors=errors,
            results=results
        )