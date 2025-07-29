from pydantic_settings import BaseSettings
from typing import Optional, List, Dict, Any
import os
from pathlib import Path


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Joulaa Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Joulaa"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    RELOAD: bool = False
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = "postgresql://joulaa_user:joulaa_password@localhost:5432/joulaa"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0
    
    # MinIO/S3
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "joulaa_admin"
    MINIO_SECRET_KEY: str = "joulaa_admin_password"
    MINIO_BUCKET_NAME: str = "joulaa-storage"
    MINIO_SECURE: bool = False
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    DEFAULT_LLM_PROVIDER: str = "anthropic"  # "openai" or "anthropic"
    
    # Email
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    FROM_EMAIL: str = "noreply@joulaa.app"
    FROM_NAME: str = "Joulaa Platform"
    SUPPORT_EMAIL: str = "support@joulaa.app"
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [
        "image/jpeg", "image/png", "image/gif", "image/webp",
        "application/pdf", "text/plain", "text/csv",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel"
    ]
    
    # Feature Flags
    ENABLE_USER_REGISTRATION: bool = True
    ENABLE_EMAIL_VERIFICATION: bool = True
    ENABLE_PASSWORD_RESET: bool = True
    ENABLE_ORGANIZATION_INVITES: bool = True
    ENABLE_AI_AGENT_STUDIO: bool = True
    ENABLE_ENTERPRISE_INTEGRATIONS: bool = False
    ENABLE_BILLING: bool = False
    ENABLE_ANALYTICS: bool = True
    
    # Security
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    MAX_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_DURATION: int = 30  # minutes
    
    # Session
    SESSION_TIMEOUT: int = 24 * 60  # minutes
    REMEMBER_ME_DURATION: int = 30  # days
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://joulaa.app",
        "https://*.joulaa.app"
    ]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    ENABLE_METRICS: bool = True
    
    # Arabic NLP
    ARABIC_MODEL_PATH: Optional[str] = None
    ARABIC_TOKENIZER_PATH: Optional[str] = None
    
    # Enterprise Integrations
    SAP_CLIENT_ID: Optional[str] = None
    SAP_CLIENT_SECRET: Optional[str] = None
    ORACLE_CLIENT_ID: Optional[str] = None
    ORACLE_CLIENT_SECRET: Optional[str] = None
    
    # Billing
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    
    # Webhooks
    WEBHOOK_SECRET: Optional[str] = None
    WEBHOOK_TIMEOUT: int = 30
    
    # Cache
    CACHE_TTL: int = 300  # 5 minutes
    CACHE_MAX_SIZE: int = 1000
    
    # Background Tasks
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    # Internationalization
    DEFAULT_LANGUAGE: str = "ar"
    SUPPORTED_LANGUAGES: List[str] = ["ar", "en"]
    DEFAULT_TIMEZONE: str = "Asia/Riyadh"
    
    # Content Moderation
    ENABLE_CONTENT_MODERATION: bool = True
    CONTENT_MODERATION_PROVIDER: str = "openai"  # openai, azure
    
    # Analytics
    GOOGLE_ANALYTICS_ID: Optional[str] = None
    MIXPANEL_TOKEN: Optional[str] = None
    
    # Health Checks
    HEALTH_CHECK_INTERVAL: int = 30  # seconds
    HEALTH_CHECK_TIMEOUT: int = 5  # seconds
    
    # Backup
    BACKUP_ENABLED: bool = False
    BACKUP_SCHEDULE: str = "0 2 * * *"  # Daily at 2 AM
    BACKUP_RETENTION_DAYS: int = 30
    
    # Compliance
    GDPR_ENABLED: bool = True
    DATA_RETENTION_DAYS: int = 365
    AUDIT_LOG_ENABLED: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Environment-specific configurations
def get_environment_config() -> Dict[str, Any]:
    """Get environment-specific configuration"""
    env = os.getenv("ENVIRONMENT", "development")
    
    configs = {
        "development": {
            "DEBUG": True,
            "RELOAD": True,
            "LOG_LEVEL": "DEBUG",
            "WORKERS": 1,
        },
        "staging": {
            "DEBUG": False,
            "RELOAD": False,
            "LOG_LEVEL": "INFO",
            "WORKERS": 2,
        },
        "production": {
            "DEBUG": False,
            "RELOAD": False,
            "LOG_LEVEL": "WARNING",
            "WORKERS": 4,
            "ENABLE_METRICS": True,
            "AUDIT_LOG_ENABLED": True,
        }
    }
    
    return configs.get(env, configs["development"])


# Validate required settings
def validate_settings():
    """Validate that all required settings are present"""
    required_settings = [
        "SECRET_KEY",
        "DATABASE_URL",
        "REDIS_URL",
    ]
    
    # Additional required settings for production
    if settings.ENVIRONMENT == "production":
        required_settings.extend([
            "SMTP_SERVER",
            "SMTP_USERNAME",
            "SMTP_PASSWORD",
            "SENTRY_DSN",
        ])
    
    missing_settings = []
    for setting in required_settings:
        value = getattr(settings, setting)
        if not value or (isinstance(value, str) and value.strip() == ""):
            missing_settings.append(setting)
    
    if missing_settings:
        raise ValueError(f"Missing required settings: {', '.join(missing_settings)}")


def is_production() -> bool:
    """Check if running in production environment"""
    return settings.ENVIRONMENT == "production"


def is_development() -> bool:
    """Check if running in development environment"""
    return settings.ENVIRONMENT == "development"


# Apply environment-specific configurations
env_config = get_environment_config()
for key, value in env_config.items():
    if hasattr(settings, key):
        setattr(settings, key, value)

# Validate on import
validate_settings()