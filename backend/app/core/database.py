from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import redis.asyncio as redis
import structlog
from typing import AsyncGenerator, Generator
import os

from .config import settings

logger = structlog.get_logger()

# Database engine
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Redis client
redis_client: redis.Redis = None


async def init_db():
    """Initialize database connection and create tables"""
    global redis_client
    
    try:
        # Initialize Redis
        redis_client = redis.from_url(
            settings.REDIS_URL,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        
        # Test Redis connection
        await redis_client.ping()
        logger.info("Redis connection established")
        
        # Skip table creation in development mode if tables already exist
        if settings.ENVIRONMENT != "development":
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
        else:
            logger.info("Skipping table creation in development mode")
        
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise


async def close_db():
    """Close database connections"""
    global redis_client
    
    try:
        if redis_client:
            await redis_client.close()
            logger.info("Redis connection closed")
    except Exception as e:
        logger.error("Error closing Redis connection", error=str(e))


def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_redis() -> redis.Redis:
    """Get Redis client"""
    if not redis_client:
        raise RuntimeError("Redis client not initialized")
    return redis_client


# Database utilities
def get_db_url() -> str:
    """Get database URL for Alembic"""
    return settings.DATABASE_URL


def create_tables():
    """Create all tables (for development)"""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all tables (for testing)"""
    Base.metadata.drop_all(bind=engine)


# Database health check
async def check_db_health() -> dict:
    """Check database health"""
    try:
        # Test PostgreSQL
        with SessionLocal() as db:
            db.execute("SELECT 1")
        
        # Test Redis
        if redis_client:
            await redis_client.ping()
        
        return {
            "status": "healthy",
            "postgresql": "connected",
            "redis": "connected"
        }
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Database migration utilities
def get_alembic_config():
    """Get Alembic configuration"""
    from alembic.config import Config
    
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "alembic")
    alembic_cfg.set_main_option("sqlalchemy.url", get_db_url())
    
    return alembic_cfg


# Database backup utilities
async def create_backup():
    """Create database backup"""
    try:
        import subprocess
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_joulaa_{timestamp}.sql"
        
        # Extract database connection details
        db_url = settings.DATABASE_URL
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "")
        
        # Create backup command
        cmd = [
            "pg_dump",
            "-h", "localhost",
            "-U", "joulaa_user",
            "-d", "joulaa",
            "-f", backup_file,
            "--no-password"
        ]
        
        # Set password environment variable
        env = os.environ.copy()
        env["PGPASSWORD"] = "joulaa_password"
        
        # Execute backup
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Database backup created successfully", file=backup_file)
            return backup_file
        else:
            logger.error("Database backup failed", error=result.stderr)
            return None
            
    except Exception as e:
        logger.error("Failed to create database backup", error=str(e))
        return None


# Database restore utilities
async def restore_backup(backup_file: str):
    """Restore database from backup"""
    try:
        import subprocess
        
        # Extract database connection details
        db_url = settings.DATABASE_URL
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "")
        
        # Create restore command
        cmd = [
            "psql",
            "-h", "localhost",
            "-U", "joulaa_user",
            "-d", "joulaa",
            "-f", backup_file,
            "--no-password"
        ]
        
        # Set password environment variable
        env = os.environ.copy()
        env["PGPASSWORD"] = "joulaa_password"
        
        # Execute restore
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Database restored successfully", file=backup_file)
            return True
        else:
            logger.error("Database restore failed", error=result.stderr)
            return False
            
    except Exception as e:
        logger.error("Failed to restore database", error=str(e))
        return False