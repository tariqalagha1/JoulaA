from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel
import os


class FeatureFlag(str, Enum):
    """Feature flags for the Joulaa platform"""
    
    # Core Features
    USER_REGISTRATION = "enable_registration"
    EMAIL_VERIFICATION = "enable_email_verification"
    TWO_FACTOR_AUTH = "enable_two_factor_auth"
    SOCIAL_LOGIN = "enable_social_login"
    
    # AI Features
    AGENT_STUDIO = "enable_agent_studio"
    CUSTOM_AGENTS = "enable_custom_agents"
    AI_ANALYTICS = "enable_ai_analytics"
    CONVERSATION_HISTORY = "enable_conversation_history"
    
    # Enterprise Features
    ENTERPRISE_INTEGRATIONS = "enable_enterprise_integrations"
    SAP_INTEGRATION = "enable_sap_integration"
    ORACLE_INTEGRATION = "enable_oracle_integration"
    MICROSOFT_INTEGRATION = "enable_microsoft_integration"
    
    # Analytics & Monitoring
    ANALYTICS = "enable_analytics"
    AUDIT_LOGS = "enable_audit_logs"
    PERFORMANCE_MONITORING = "enable_performance_monitoring"
    ERROR_TRACKING = "enable_error_tracking"
    
    # Billing & Subscriptions
    BILLING = "enable_billing"
    SUBSCRIPTION_MANAGEMENT = "enable_subscription_management"
    USAGE_TRACKING = "enable_usage_tracking"
    
    # Security Features
    RATE_LIMITING = "enable_rate_limiting"
    IP_WHITELISTING = "enable_ip_whitelisting"
    ADVANCED_SECURITY = "enable_advanced_security"
    
    # Regional Features
    ARABIC_NLP = "enable_arabic_nlp"
    RTL_SUPPORT = "enable_rtl_support"
    REGIONAL_COMPLIANCE = "enable_regional_compliance"
    
    # Development Features
    DEBUG_MODE = "enable_debug_mode"
    API_DOCS = "enable_api_docs"
    PROFILING = "enable_profiling"


class FeatureFlagConfig(BaseModel):
    """Configuration for feature flags"""
    
    name: str
    description: str
    default_value: bool
    environment_dependent: bool = False
    requires_restart: bool = False
    category: str = "general"


class FeatureFlagManager:
    """Manages feature flags for the application"""
    
    def __init__(self):
        self._flags: Dict[FeatureFlag, FeatureFlagConfig] = {
            # Core Features
            FeatureFlag.USER_REGISTRATION: FeatureFlagConfig(
                name="User Registration",
                description="Allow new users to register accounts",
                default_value=True,
                category="authentication"
            ),
            FeatureFlag.EMAIL_VERIFICATION: FeatureFlagConfig(
                name="Email Verification",
                description="Require email verification for new accounts",
                default_value=True,
                category="authentication"
            ),
            FeatureFlag.TWO_FACTOR_AUTH: FeatureFlagConfig(
                name="Two-Factor Authentication",
                description="Enable 2FA for enhanced security",
                default_value=False,
                category="security"
            ),
            FeatureFlag.SOCIAL_LOGIN: FeatureFlagConfig(
                name="Social Login",
                description="Allow login with social media accounts",
                default_value=False,
                category="authentication"
            ),
            
            # AI Features
            FeatureFlag.AGENT_STUDIO: FeatureFlagConfig(
                name="Agent Studio",
                description="Low-code agent builder interface",
                default_value=True,
                category="ai"
            ),
            FeatureFlag.CUSTOM_AGENTS: FeatureFlagConfig(
                name="Custom Agents",
                description="Allow users to create custom AI agents",
                default_value=True,
                category="ai"
            ),
            FeatureFlag.AI_ANALYTICS: FeatureFlagConfig(
                name="AI Analytics",
                description="Advanced analytics for AI interactions",
                default_value=True,
                category="ai"
            ),
            FeatureFlag.CONVERSATION_HISTORY: FeatureFlagConfig(
                name="Conversation History",
                description="Store and retrieve conversation history",
                default_value=True,
                category="ai"
            ),
            
            # Enterprise Features
            FeatureFlag.ENTERPRISE_INTEGRATIONS: FeatureFlagConfig(
                name="Enterprise Integrations",
                description="Connect with enterprise systems",
                default_value=True,
                category="enterprise"
            ),
            FeatureFlag.SAP_INTEGRATION: FeatureFlagConfig(
                name="SAP Integration",
                description="Connect with SAP systems",
                default_value=False,
                category="enterprise"
            ),
            FeatureFlag.ORACLE_INTEGRATION: FeatureFlagConfig(
                name="Oracle Integration",
                description="Connect with Oracle systems",
                default_value=False,
                category="enterprise"
            ),
            FeatureFlag.MICROSOFT_INTEGRATION: FeatureFlagConfig(
                name="Microsoft Integration",
                description="Connect with Microsoft 365/Azure",
                default_value=False,
                category="enterprise"
            ),
            
            # Analytics & Monitoring
            FeatureFlag.ANALYTICS: FeatureFlagConfig(
                name="Analytics",
                description="User and system analytics",
                default_value=True,
                category="monitoring"
            ),
            FeatureFlag.AUDIT_LOGS: FeatureFlagConfig(
                name="Audit Logs",
                description="Detailed audit logging",
                default_value=True,
                category="monitoring"
            ),
            FeatureFlag.PERFORMANCE_MONITORING: FeatureFlagConfig(
                name="Performance Monitoring",
                description="Monitor application performance",
                default_value=True,
                environment_dependent=True,
                category="monitoring"
            ),
            FeatureFlag.ERROR_TRACKING: FeatureFlagConfig(
                name="Error Tracking",
                description="Track and report errors",
                default_value=True,
                category="monitoring"
            ),
            
            # Billing & Subscriptions
            FeatureFlag.BILLING: FeatureFlagConfig(
                name="Billing",
                description="Enable billing and payments",
                default_value=False,
                category="billing"
            ),
            FeatureFlag.SUBSCRIPTION_MANAGEMENT: FeatureFlagConfig(
                name="Subscription Management",
                description="Manage user subscriptions",
                default_value=False,
                category="billing"
            ),
            FeatureFlag.USAGE_TRACKING: FeatureFlagConfig(
                name="Usage Tracking",
                description="Track API and feature usage",
                default_value=True,
                category="billing"
            ),
            
            # Security Features
            FeatureFlag.RATE_LIMITING: FeatureFlagConfig(
                name="Rate Limiting",
                description="Limit API request rates",
                default_value=True,
                category="security"
            ),
            FeatureFlag.IP_WHITELISTING: FeatureFlagConfig(
                name="IP Whitelisting",
                description="Restrict access by IP address",
                default_value=False,
                category="security"
            ),
            FeatureFlag.ADVANCED_SECURITY: FeatureFlagConfig(
                name="Advanced Security",
                description="Enhanced security features",
                default_value=False,
                category="security"
            ),
            
            # Regional Features
            FeatureFlag.ARABIC_NLP: FeatureFlagConfig(
                name="Arabic NLP",
                description="Advanced Arabic language processing",
                default_value=True,
                category="regional"
            ),
            FeatureFlag.RTL_SUPPORT: FeatureFlagConfig(
                name="RTL Support",
                description="Right-to-left language support",
                default_value=True,
                category="regional"
            ),
            FeatureFlag.REGIONAL_COMPLIANCE: FeatureFlagConfig(
                name="Regional Compliance",
                description="MENA region compliance features",
                default_value=True,
                category="regional"
            ),
            
            # Development Features
            FeatureFlag.DEBUG_MODE: FeatureFlagConfig(
                name="Debug Mode",
                description="Enable debug features",
                default_value=False,
                environment_dependent=True,
                requires_restart=True,
                category="development"
            ),
            FeatureFlag.API_DOCS: FeatureFlagConfig(
                name="API Documentation",
                description="Enable API documentation endpoints",
                default_value=False,
                environment_dependent=True,
                requires_restart=True,
                category="development"
            ),
            FeatureFlag.PROFILING: FeatureFlagConfig(
                name="Profiling",
                description="Enable application profiling",
                default_value=False,
                environment_dependent=True,
                requires_restart=True,
                category="development"
            ),
        }
    
    def is_enabled(self, flag: FeatureFlag) -> bool:
        """Check if a feature flag is enabled"""
        env_var = flag.value.upper()
        env_value = os.getenv(env_var)
        
        if env_value is not None:
            return env_value.lower() in ('true', '1', 'yes', 'on')
        
        return self._flags[flag].default_value
    
    def get_config(self, flag: FeatureFlag) -> FeatureFlagConfig:
        """Get configuration for a feature flag"""
        return self._flags[flag]
    
    def get_all_flags(self) -> Dict[str, Dict[str, Any]]:
        """Get all feature flags with their current status"""
        result = {}
        for flag, config in self._flags.items():
            result[flag.value] = {
                "name": config.name,
                "description": config.description,
                "enabled": self.is_enabled(flag),
                "default_value": config.default_value,
                "environment_dependent": config.environment_dependent,
                "requires_restart": config.requires_restart,
                "category": config.category
            }
        return result
    
    def get_flags_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """Get feature flags filtered by category"""
        all_flags = self.get_all_flags()
        return {
            flag: config for flag, config in all_flags.items()
            if config["category"] == category
        }


# Global feature flag manager instance
feature_flags = FeatureFlagManager()


# Convenience functions
def is_feature_enabled(flag: FeatureFlag) -> bool:
    """Check if a feature is enabled"""
    return feature_flags.is_enabled(flag)


def require_feature(flag: FeatureFlag):
    """Decorator to require a feature flag to be enabled"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not is_feature_enabled(flag):
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=403,
                    detail=f"Feature '{flag.value}' is not enabled"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator