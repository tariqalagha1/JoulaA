import asyncio
import json
import time
from typing import Dict, Any, List, Optional, AsyncGenerator, Tuple
from uuid import UUID
import structlog
from datetime import datetime

import openai
import anthropic
from arabic_reshaper import reshape
from bidi.algorithm import get_display

from ..core.config import settings
from ..models.agent import AIAgent, AgentType, AgentCapability
from ..schemas.agent import AgentChatRequest, AgentChatResponse
from ..core.feature_flags import is_feature_enabled, FeatureFlag

logger = structlog.get_logger()


class ArabicTextProcessor:
    """Handles Arabic text processing and formatting"""
    
    @staticmethod
    def preprocess_arabic_text(text: str) -> str:
        """Preprocess Arabic text for better LLM understanding"""
        if not text or not is_feature_enabled(FeatureFlag.ARABIC_NLP):
            return text
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Normalize Arabic characters
        text = text.replace('ي', 'ی').replace('ك', 'ک')
        
        # Handle Arabic numerals if enabled
        if is_feature_enabled(FeatureFlag.RTL_SUPPORT):
            # Convert Western numerals to Arabic numerals
            western_to_arabic = str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩')
            text = text.translate(western_to_arabic)
        
        return text
    
    @staticmethod
    def format_arabic_response(text: str) -> str:
        """Format Arabic text for RTL display"""
        if not text or not is_feature_enabled(FeatureFlag.RTL_SUPPORT):
            return text
        
        try:
            # Reshape Arabic text for proper display
            reshaped_text = reshape(text)
            # Apply bidirectional algorithm
            display_text = get_display(reshaped_text)
            return display_text
        except Exception as e:
            logger.warning("Failed to format Arabic text", error=str(e))
            return text
    
    @staticmethod
    def detect_language(text: str) -> str:
        """Detect if text is Arabic or English"""
        arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
        total_chars = len([char for char in text if char.isalpha()])
        
        if total_chars == 0:
            return 'en'
        
        arabic_ratio = arabic_chars / total_chars
        return 'ar' if arabic_ratio > 0.3 else 'en'


class LLMProvider:
    """Base class for LLM providers"""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.arabic_processor = ArabicTextProcessor()
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        agent: AIAgent,
        **kwargs
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate response from LLM"""
        raise NotImplementedError
    
    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        agent: AIAgent,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream response from LLM"""
        raise NotImplementedError
    
    def prepare_messages(
        self,
        messages: List[Dict[str, str]],
        agent: AIAgent,
        language: str = 'ar'
    ) -> List[Dict[str, str]]:
        """Prepare messages for LLM with agent context"""
        prepared_messages = []
        
        # Add system prompt
        system_prompt = self._get_system_prompt(agent, language)
        if system_prompt:
            prepared_messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Process and add conversation messages
        for message in messages:
            content = message.get("content", "")
            if language == 'ar' and is_feature_enabled(FeatureFlag.ARABIC_NLP):
                content = self.arabic_processor.preprocess_arabic_text(content)
            
            prepared_messages.append({
                "role": message.get("role", "user"),
                "content": content
            })
        
        return prepared_messages
    
    def _get_system_prompt(self, agent: AIAgent, language: str) -> str:
        """Get system prompt for agent in specified language"""
        if language == 'ar' and agent.system_prompt_ar:
            return agent.system_prompt_ar
        elif language == 'en' and agent.system_prompt_en:
            return agent.system_prompt_en
        
        # Default system prompt based on agent type
        default_prompts = {
            AgentType.FINANCE: {
                'ar': 'أنت مساعد ذكي متخصص في الشؤون المالية. تساعد في تحليل البيانات المالية وإعداد التقارير والميزانيات.',
                'en': 'You are an AI assistant specialized in finance. You help with financial analysis, reporting, and budgeting.'
            },
            AgentType.PROCUREMENT: {
                'ar': 'أنت مساعد ذكي متخصص في المشتريات والتوريد. تساعد في مقارنة العروض وإدارة الموردين.',
                'en': 'You are an AI assistant specialized in procurement. You help with vendor comparison and supplier management.'
            },
            AgentType.HR: {
                'ar': 'أنت مساعد ذكي متخصص في الموارد البشرية. تساعد في إدارة الموظفين وتقييم الأداء.',
                'en': 'You are an AI assistant specialized in human resources. You help with employee management and performance evaluation.'
            },
            AgentType.SUPPLY_CHAIN: {
                'ar': 'أنت مساعد ذكي متخصص في سلسلة التوريد. تساعد في تتبع الشحنات وإدارة المخزون.',
                'en': 'You are an AI assistant specialized in supply chain. You help with shipment tracking and inventory management.'
            },
            AgentType.CUSTOMER_SERVICE: {
                'ar': 'أنت مساعد ذكي متخصص في خدمة العملاء. تساعد في حل مشاكل العملاء وتقديم الدعم.',
                'en': 'You are an AI assistant specialized in customer service. You help resolve customer issues and provide support.'
            }
        }
        
        agent_prompts = default_prompts.get(agent.agent_type, {})
        return agent_prompts.get(language, agent_prompts.get('en', ''))


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider"""
    
    def __init__(self):
        super().__init__("openai")
        # Skip real API connection in development
        if settings.ENVIRONMENT == "development" and (settings.OPENAI_API_KEY is None or "placeholder" in settings.OPENAI_API_KEY):
            self.client = None
        else:
            self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        agent: AIAgent,
        **kwargs
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate response using OpenAI"""
        # Return mock response in development mode
        if self.client is None:
            language = kwargs.get('language', 'ar')
            mock_response = "مرحباً! هذا رد تجريبي من منصة جولة. النظام يعمل في وضع التطوير." if language == 'ar' else "Hello! This is a mock response from Joulaa Platform. System is running in development mode."
            return mock_response, {
                "model": "mock-openai",
                "tokens_used": 50,
                "response_time": 0.5,
                "provider": "openai-mock"
            }
        
        try:
            language = kwargs.get('language', 'ar')
            prepared_messages = self.prepare_messages(messages, agent, language)
            
            response = await self.client.chat.completions.create(
                model=agent.llm_model or "gpt-4",
                messages=prepared_messages,
                max_tokens=int(agent.max_tokens or 4000),
                temperature=float(agent.temperature or 0.7),
                **kwargs
            )
            
            content = response.choices[0].message.content
            
            # Format Arabic response if needed
            if language == 'ar':
                content = self.arabic_processor.format_arabic_response(content)
            
            metadata = {
                "model": response.model,
                "tokens_used": response.usage.total_tokens,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "finish_reason": response.choices[0].finish_reason
            }
            
            return content, metadata
            
        except Exception as e:
            logger.error("OpenAI API error", error=str(e), agent_id=agent.id)
            raise
    
    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        agent: AIAgent,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream response using OpenAI"""
        try:
            language = kwargs.get('language', 'ar')
            prepared_messages = self.prepare_messages(messages, agent, language)
            
            stream = await self.client.chat.completions.create(
                model=agent.llm_model or "gpt-4",
                messages=prepared_messages,
                max_tokens=int(agent.max_tokens or 4000),
                temperature=float(agent.temperature or 0.7),
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    if language == 'ar':
                        content = self.arabic_processor.format_arabic_response(content)
                    yield content
                    
        except Exception as e:
            logger.error("OpenAI streaming error", error=str(e), agent_id=agent.id)
            raise


class AnthropicProvider(LLMProvider):
    """Anthropic Claude LLM provider"""
    
    def __init__(self):
        super().__init__("anthropic")
        # Skip real API connection in development
        if settings.ENVIRONMENT == "development" and (settings.ANTHROPIC_API_KEY is None or "placeholder" in settings.ANTHROPIC_API_KEY):
            self.client = None
        else:
            self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        agent: AIAgent,
        **kwargs
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate response using Anthropic Claude"""
        # Return mock response in development mode
        if self.client is None:
            language = kwargs.get('language', 'ar')
            mock_response = "مرحباً! هذا رد تجريبي من منصة جولة باستخدام Claude. النظام يعمل في وضع التطوير." if language == 'ar' else "Hello! This is a mock response from Joulaa Platform using Claude. System is running in development mode."
            return mock_response, {
                "model": "mock-claude",
                "tokens_used": 55,
                "response_time": 0.6,
                "provider": "anthropic-mock"
            }
        
        try:
            language = kwargs.get('language', 'ar')
            prepared_messages = self.prepare_messages(messages, agent, language)
            
            # Extract system message for Claude
            system_message = ""
            user_messages = []
            
            for msg in prepared_messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    user_messages.append(msg)
            
            response = await self.client.messages.create(
                model=agent.llm_model or "claude-3-sonnet-20240229",
                system=system_message,
                messages=user_messages,
                max_tokens=int(agent.max_tokens or 4000),
                temperature=float(agent.temperature or 0.7),
                **kwargs
            )
            
            content = response.content[0].text
            
            # Format Arabic response if needed
            if language == 'ar':
                content = self.arabic_processor.format_arabic_response(content)
            
            metadata = {
                "model": response.model,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "stop_reason": response.stop_reason
            }
            
            return content, metadata
            
        except Exception as e:
            logger.error("Anthropic API error", error=str(e), agent_id=agent.id)
            raise
    
    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        agent: AIAgent,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream response using Anthropic Claude"""
        try:
            language = kwargs.get('language', 'ar')
            prepared_messages = self.prepare_messages(messages, agent, language)
            
            # Extract system message for Claude
            system_message = ""
            user_messages = []
            
            for msg in prepared_messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    user_messages.append(msg)
            
            async with self.client.messages.stream(
                model=agent.llm_model or "claude-3-sonnet-20240229",
                system=system_message,
                messages=user_messages,
                max_tokens=int(agent.max_tokens or 4000),
                temperature=float(agent.temperature or 0.7),
                **kwargs
            ) as stream:
                async for text in stream.text_stream:
                    if language == 'ar':
                        text = self.arabic_processor.format_arabic_response(text)
                    yield text
                    
        except Exception as e:
            logger.error("Anthropic streaming error", error=str(e), agent_id=agent.id)
            raise


class AIService:
    """Main AI service for handling agent interactions"""
    
    def __init__(self):
        self.providers = {
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider()
        }
        self.arabic_processor = ArabicTextProcessor()
    
    def get_provider(self, provider_name: str) -> LLMProvider:
        """Get LLM provider by name"""
        if provider_name not in self.providers:
            raise ValueError(f"Unsupported LLM provider: {provider_name}")
        return self.providers[provider_name]
    
    async def chat_with_agent(
        self,
        agent: AIAgent,
        request: AgentChatRequest,
        conversation_history: List[Dict[str, str]] = None
    ) -> AgentChatResponse:
        """Chat with an AI agent"""
        start_time = time.time()
        
        try:
            # Detect language if not specified
            language = request.language
            if not language:
                language = self.arabic_processor.detect_language(request.message)
            
            # Prepare conversation messages
            messages = conversation_history or []
            messages.append({
                "role": "user",
                "content": request.message
            })
            
            # Get LLM provider
            provider = self.get_provider(agent.llm_provider)
            
            # Generate response
            response_content, metadata = await provider.generate_response(
                messages=messages,
                agent=agent,
                language=language,
                **request.context
            )
            
            response_time = time.time() - start_time
            
            # Create response
            response = AgentChatResponse(
                message=response_content,
                language=language,
                conversation_id=request.conversation_id or UUID('00000000-0000-0000-0000-000000000000'),
                message_id=UUID('00000000-0000-0000-0000-000000000000'),  # Would be generated in real implementation
                agent_id=agent.id,
                response_time=response_time,
                tokens_used=metadata.get('tokens_used', 0),
                confidence_score=self._calculate_confidence_score(metadata),
                suggested_actions=self._generate_suggested_actions(agent, response_content, language),
                metadata=metadata,
                created_at=datetime.utcnow()
            )
            
            logger.info(
                "Agent response generated",
                agent_id=agent.id,
                response_time=response_time,
                tokens_used=metadata.get('tokens_used', 0),
                language=language
            )
            
            return response
            
        except Exception as e:
            logger.error(
                "Failed to generate agent response",
                agent_id=agent.id,
                error=str(e),
                exc_info=True
            )
            raise
    
    async def stream_chat_with_agent(
        self,
        agent: AIAgent,
        request: AgentChatRequest,
        conversation_history: List[Dict[str, str]] = None
    ) -> AsyncGenerator[str, None]:
        """Stream chat with an AI agent"""
        try:
            # Detect language if not specified
            language = request.language
            if not language:
                language = self.arabic_processor.detect_language(request.message)
            
            # Prepare conversation messages
            messages = conversation_history or []
            messages.append({
                "role": "user",
                "content": request.message
            })
            
            # Get LLM provider
            provider = self.get_provider(agent.llm_provider)
            
            # Stream response
            async for chunk in provider.stream_response(
                messages=messages,
                agent=agent,
                language=language,
                **request.context
            ):
                yield chunk
                
        except Exception as e:
            logger.error(
                "Failed to stream agent response",
                agent_id=agent.id,
                error=str(e),
                exc_info=True
            )
            raise
    
    def _calculate_confidence_score(self, metadata: Dict[str, Any]) -> float:
        """Calculate confidence score based on response metadata"""
        # Simple confidence calculation based on token usage and finish reason
        tokens_used = metadata.get('tokens_used', 0)
        max_tokens = metadata.get('max_tokens', 4000)
        finish_reason = metadata.get('finish_reason') or metadata.get('stop_reason')
        
        # Base confidence
        confidence = 0.8
        
        # Adjust based on token usage
        if tokens_used > max_tokens * 0.9:
            confidence -= 0.2  # Response was cut off
        
        # Adjust based on finish reason
        if finish_reason in ['stop', 'end_turn']:
            confidence += 0.1
        elif finish_reason in ['length', 'max_tokens']:
            confidence -= 0.1
        
        return max(0.0, min(1.0, confidence))
    
    def _generate_suggested_actions(
        self,
        agent: AIAgent,
        response_content: str,
        language: str
    ) -> List[Dict[str, Any]]:
        """Generate suggested actions based on agent type and response"""
        actions = []
        
        # Common actions for all agents
        if language == 'ar':
            actions.append({
                "type": "clarify",
                "label": "اطلب توضيحاً",
                "description": "اطلب مزيداً من التفاصيل حول هذا الموضوع"
            })
            actions.append({
                "type": "continue",
                "label": "تابع المحادثة",
                "description": "اسأل سؤالاً متابعاً"
            })
        else:
            actions.append({
                "type": "clarify",
                "label": "Ask for clarification",
                "description": "Request more details about this topic"
            })
            actions.append({
                "type": "continue",
                "label": "Continue conversation",
                "description": "Ask a follow-up question"
            })
        
        # Agent-specific actions
        if agent.agent_type == AgentType.FINANCE:
            if language == 'ar':
                actions.append({
                    "type": "generate_report",
                    "label": "إنشاء تقرير",
                    "description": "إنشاء تقرير مالي مفصل"
                })
            else:
                actions.append({
                    "type": "generate_report",
                    "label": "Generate Report",
                    "description": "Create a detailed financial report"
                })
        
        elif agent.agent_type == AgentType.PROCUREMENT:
            if language == 'ar':
                actions.append({
                    "type": "compare_vendors",
                    "label": "مقارنة الموردين",
                    "description": "مقارنة عروض الموردين المختلفين"
                })
            else:
                actions.append({
                    "type": "compare_vendors",
                    "label": "Compare Vendors",
                    "description": "Compare different vendor proposals"
                })
        
        return actions


# Global AI service instance
ai_service = AIService()