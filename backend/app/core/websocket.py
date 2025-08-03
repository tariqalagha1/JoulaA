import asyncio
import json
from typing import Dict, List, Optional, Set
from uuid import UUID
import structlog
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from ..services.conversation_service import ConversationService
from ..services.ai_service import ai_service
from ..models.user import User
from ..schemas.conversation import MessageCreate, ChatRequest
from .auth import get_user_from_token
from .database import get_db

logger = structlog.get_logger()


class ConnectionManager:
    """Manages WebSocket connections for real-time chat"""
    
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Store conversation participants
        self.conversation_participants: Dict[str, Set[str]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        
        logger.info(
            "WebSocket connection established",
            user_id=user_id,
            total_connections=len(self.active_connections.get(user_id, []))
        )
        
    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            
            # Clean up empty connection sets
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        logger.info(
            "WebSocket connection closed",
            user_id=user_id,
            remaining_connections=len(self.active_connections.get(user_id, []))
        )
        
    async def send_personal_message(self, message: dict, user_id: str):
        """Send a message to all connections of a specific user"""
        if user_id in self.active_connections:
            disconnected_websockets = []
            
            for websocket in self.active_connections[user_id].copy():
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.warning(
                        "Failed to send message to WebSocket",
                        user_id=user_id,
                        error=str(e)
                    )
                    disconnected_websockets.append(websocket)
            
            # Clean up disconnected websockets
            for websocket in disconnected_websockets:
                self.active_connections[user_id].discard(websocket)
                
    async def join_conversation(self, user_id: str, conversation_id: str):
        """Add user to conversation participants"""
        if conversation_id not in self.conversation_participants:
            self.conversation_participants[conversation_id] = set()
        
        self.conversation_participants[conversation_id].add(user_id)
        
        logger.info(
            "User joined conversation",
            user_id=user_id,
            conversation_id=conversation_id
        )
        
    async def leave_conversation(self, user_id: str, conversation_id: str):
        """Remove user from conversation participants"""
        if conversation_id in self.conversation_participants:
            self.conversation_participants[conversation_id].discard(user_id)
            
            # Clean up empty conversation sets
            if not self.conversation_participants[conversation_id]:
                del self.conversation_participants[conversation_id]
        
        logger.info(
            "User left conversation",
            user_id=user_id,
            conversation_id=conversation_id
        )
        
    async def broadcast_to_conversation(self, message: dict, conversation_id: str, exclude_user: Optional[str] = None):
        """Broadcast a message to all participants in a conversation"""
        if conversation_id not in self.conversation_participants:
            return
            
        participants = self.conversation_participants[conversation_id]
        
        for user_id in participants:
            if exclude_user and user_id == exclude_user:
                continue
                
            await self.send_personal_message(message, user_id)


# Global connection manager instance
connection_manager = ConnectionManager()


class WebSocketHandler:
    """Handles WebSocket message processing"""
    
    def __init__(self, db: AsyncSession, user: User, websocket: WebSocket):
        self.db = db
        self.user = user
        self.websocket = websocket
        self.conversation_service = ConversationService(db)
        
    async def handle_message(self, data: dict):
        """Process incoming WebSocket messages"""
        message_type = data.get('type')
        
        try:
            if message_type == 'send_message':
                await self._handle_send_message(data)
            elif message_type == 'join_conversation':
                await self._handle_join_conversation(data)
            elif message_type == 'leave_conversation':
                await self._handle_leave_conversation(data)
            elif message_type == 'typing':
                await self._handle_typing(data)
            else:
                await self._send_error(f"Unknown message type: {message_type}")
                
        except Exception as e:
            logger.error(
                "Error handling WebSocket message",
                user_id=str(self.user.id),
                message_type=message_type,
                error=str(e),
                exc_info=True
            )
            await self._send_error("Internal server error")
            
    async def _handle_send_message(self, data: dict):
        """Handle sending a new message"""
        conversation_id = data.get('conversation_id')
        message_content = data.get('message')
        agent_id = data.get('agent_id')
        
        if not conversation_id or not message_content:
            await self._send_error("Missing conversation_id or message")
            return
            
        try:
            # Create user message
            message_data = MessageCreate(
                content=message_content,
                role='user',
                conversation_id=UUID(conversation_id)
            )
            
            user_message = await self.conversation_service.add_message(
                conversation_id=UUID(conversation_id),
                message_data=message_data,
                user_id=self.user.id
            )
            
            # Broadcast user message to conversation participants
            await connection_manager.broadcast_to_conversation(
                {
                    'type': 'new_message',
                    'message': {
                        'id': str(user_message.id),
                        'content': user_message.content,
                        'role': user_message.role,
                        'conversation_id': str(user_message.conversation_id),
                        'created_at': user_message.created_at.isoformat(),
                        'user_id': str(user_message.user_id)
                    }
                },
                conversation_id
            )
            
            # Generate AI response if agent_id is provided
            if agent_id:
                await self._generate_ai_response(conversation_id, agent_id, message_content)
                
        except Exception as e:
            logger.error(
                "Error sending message",
                user_id=str(self.user.id),
                conversation_id=conversation_id,
                error=str(e)
            )
            await self._send_error("Failed to send message")
            
    async def _generate_ai_response(self, conversation_id: str, agent_id: str, user_message: str):
        """Generate and stream AI response"""
        try:
            # Get agent and conversation history
            agent = await self.conversation_service.get_agent_for_conversation(
                conversation_id=UUID(conversation_id),
                agent_id=UUID(agent_id)
            )
            
            if not agent:
                await self._send_error("Agent not found")
                return
                
            # Get conversation history
            messages = await self.conversation_service.get_conversation_messages(
                conversation_id=UUID(conversation_id),
                limit=20
            )
            
            # Prepare chat request
            chat_request = ChatRequest(
                message=user_message,
                conversation_id=UUID(conversation_id),
                agent_id=UUID(agent_id)
            )
            
            # Stream AI response
            response_content = ""
            
            async for chunk in ai_service.stream_chat_with_agent(
                agent=agent,
                request=chat_request,
                conversation_history=[{
                    'role': msg.role,
                    'content': msg.content
                } for msg in messages]
            ):
                response_content += chunk
                
                # Send chunk to conversation participants
                await connection_manager.broadcast_to_conversation(
                    {
                        'type': 'message_chunk',
                        'chunk': chunk,
                        'conversation_id': conversation_id
                    },
                    conversation_id
                )
                
            # Save complete AI response
            ai_message_data = MessageCreate(
                content=response_content,
                role='assistant',
                conversation_id=UUID(conversation_id),
                agent_id=UUID(agent_id)
            )
            
            ai_message = await self.conversation_service.add_message(
                conversation_id=UUID(conversation_id),
                message_data=ai_message_data,
                user_id=self.user.id
            )
            
            # Send complete message
            await connection_manager.broadcast_to_conversation(
                {
                    'type': 'message_complete',
                    'message': {
                        'id': str(ai_message.id),
                        'content': ai_message.content,
                        'role': ai_message.role,
                        'conversation_id': str(ai_message.conversation_id),
                        'created_at': ai_message.created_at.isoformat(),
                        'agent_id': str(ai_message.agent_id) if ai_message.agent_id else None
                    },
                    'conversation_id': conversation_id
                },
                conversation_id
            )
            
        except Exception as e:
            logger.error(
                "Error generating AI response",
                user_id=str(self.user.id),
                conversation_id=conversation_id,
                agent_id=agent_id,
                error=str(e)
            )
            await self._send_error("Failed to generate AI response")
            
    async def _handle_join_conversation(self, data: dict):
        """Handle joining a conversation"""
        conversation_id = data.get('conversation_id')
        
        if not conversation_id:
            await self._send_error("Missing conversation_id")
            return
            
        await connection_manager.join_conversation(str(self.user.id), conversation_id)
        
        await self._send_success({
            'type': 'joined_conversation',
            'conversation_id': conversation_id
        })
        
    async def _handle_leave_conversation(self, data: dict):
        """Handle leaving a conversation"""
        conversation_id = data.get('conversation_id')
        
        if not conversation_id:
            await self._send_error("Missing conversation_id")
            return
            
        await connection_manager.leave_conversation(str(self.user.id), conversation_id)
        
        await self._send_success({
            'type': 'left_conversation',
            'conversation_id': conversation_id
        })
        
    async def _handle_typing(self, data: dict):
        """Handle typing indicator"""
        conversation_id = data.get('conversation_id')
        is_typing = data.get('is_typing', False)
        
        if not conversation_id:
            await self._send_error("Missing conversation_id")
            return
            
        # Broadcast typing status to other participants
        await connection_manager.broadcast_to_conversation(
            {
                'type': 'typing',
                'user_id': str(self.user.id),
                'is_typing': is_typing,
                'conversation_id': conversation_id
            },
            conversation_id,
            exclude_user=str(self.user.id)
        )
        
    async def _send_error(self, message: str):
        """Send error message to client"""
        await self.websocket.send_text(json.dumps({
            'type': 'error',
            'message': message
        }))
        
    async def _send_success(self, data: dict):
        """Send success message to client"""
        await self.websocket.send_text(json.dumps({
            'type': 'success',
            **data
        }))