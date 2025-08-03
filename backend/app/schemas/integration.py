from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid


class IntegrationType(str, Enum):
    """Supported integration types"""
    SAP = "sap"
    ORACLE = "oracle"
    ODOO = "odoo"
    MICROSOFT = "microsoft"
    SALESFORCE = "salesforce"
    CUSTOM = "custom"
    API = "api"
    DATABASE = "database"
    FILE = "file"
    WEBHOOK = "webhook"


class SyncStatus(str, Enum):
    """Synchronization status options"""
    PENDING = "pending"
    SYNCING = "syncing"
    SUCCESS = "success"
    ERROR = "error"
    CANCELLED = "cancelled"


class HealthStatus(str, Enum):
    """Health status options"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    DEGRADED = "degraded"


class IntegrationBase(BaseModel):
    """Base schema for integration"""
    integration_type: IntegrationType = Field(..., description="Type of integration")
    name: str = Field(..., min_length=1, max_length=255, description="Integration name")
    description: Optional[str] = Field(None, max_length=1000, description="Integration description")
    configuration: Dict[str, Any] = Field(default_factory=dict, description="Integration configuration")
    is_active: bool = Field(default=True, description="Whether integration is active")
    health_check_url: Optional[str] = Field(None, max_length=500, description="Health check endpoint URL")
    metadata_: Optional[Dict[str, Any]] = Field(default_factory=dict, alias="metadata", description="Additional metadata")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Integration name cannot be empty')
        return v.strip()
    
    @validator('configuration')
    def validate_configuration(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Configuration must be a dictionary')
        return v


class IntegrationCreate(IntegrationBase):
    """Schema for creating integration"""
    organization_id: uuid.UUID = Field(..., description="Organization ID")
    
    class Config:
        json_encoders = {
            uuid.UUID: str
        }


class IntegrationUpdate(BaseModel):
    """Schema for updating integration"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    configuration: Optional[Dict[str, Any]] = Field(None)
    is_active: Optional[bool] = Field(None)
    health_check_url: Optional[str] = Field(None, max_length=500)
    metadata_: Optional[Dict[str, Any]] = Field(None, alias="metadata")
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Integration name cannot be empty')
        return v.strip() if v else v


class IntegrationResponse(IntegrationBase):
    """Schema for integration response"""
    id: uuid.UUID
    organization_id: uuid.UUID
    sync_status: Optional[SyncStatus] = None
    sync_error: Optional[str] = None
    last_sync_at: Optional[datetime] = None
    health_status: Optional[HealthStatus] = None
    last_health_check: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[uuid.UUID] = None
    updated_by: Optional[uuid.UUID] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            uuid.UUID: str,
            datetime: lambda v: v.isoformat()
        }


class IntegrationDetailResponse(IntegrationResponse):
    """Detailed integration response with additional information"""
    display_name: str
    is_healthy: bool
    needs_sync: bool
    
    class Config:
        from_attributes = True


class IntegrationListResponse(BaseModel):
    """Schema for paginated integration list"""
    integrations: List[IntegrationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class IntegrationStats(BaseModel):
    """Schema for integration statistics"""
    total_integrations: int
    active_integrations: int
    inactive_integrations: int
    healthy_integrations: int
    unhealthy_integrations: int
    integrations_by_type: Dict[str, int]
    recent_sync_errors: int
    last_sync_summary: Dict[str, Any]


class IntegrationSyncRequest(BaseModel):
    """Schema for triggering integration sync"""
    force: bool = Field(default=False, description="Force sync even if recently synced")
    sync_type: Optional[str] = Field(None, description="Type of sync to perform")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Sync options")


class IntegrationSyncResponse(BaseModel):
    """Schema for sync response"""
    integration_id: uuid.UUID
    sync_started: bool
    sync_status: SyncStatus
    message: str
    estimated_duration: Optional[int] = None  # in seconds
    
    class Config:
        json_encoders = {
            uuid.UUID: str
        }


class IntegrationHealthCheck(BaseModel):
    """Schema for health check response"""
    integration_id: uuid.UUID
    health_status: HealthStatus
    response_time: Optional[float] = None  # in milliseconds
    error_message: Optional[str] = None
    checked_at: datetime
    details: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            uuid.UUID: str,
            datetime: lambda v: v.isoformat()
        }


class IntegrationTestRequest(BaseModel):
    """Schema for testing integration connection"""
    configuration: Dict[str, Any] = Field(..., description="Configuration to test")
    integration_type: IntegrationType = Field(..., description="Type of integration")
    test_type: Optional[str] = Field("connection", description="Type of test to perform")


class IntegrationTestResponse(BaseModel):
    """Schema for integration test response"""
    success: bool
    message: str
    response_time: Optional[float] = None
    error_details: Optional[Dict[str, Any]] = None
    test_results: Optional[Dict[str, Any]] = None


class BulkIntegrationOperation(BaseModel):
    """Schema for bulk operations on integrations"""
    integration_ids: List[uuid.UUID] = Field(..., min_items=1, max_items=100)
    operation: str = Field(..., description="Operation to perform: activate, deactivate, sync, delete")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('operation')
    def validate_operation(cls, v):
        allowed_operations = ['activate', 'deactivate', 'sync', 'delete', 'health_check']
        if v not in allowed_operations:
            raise ValueError(f'Operation must be one of: {", ".join(allowed_operations)}')
        return v
    
    class Config:
        json_encoders = {
            uuid.UUID: str
        }


class BulkIntegrationOperationResponse(BaseModel):
    """Schema for bulk operation response"""
    operation: str
    total_requested: int
    successful: int
    failed: int
    results: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]


class IntegrationSearchRequest(BaseModel):
    """Schema for searching integrations"""
    query: Optional[str] = Field(None, description="Search query")
    integration_type: Optional[IntegrationType] = Field(None, description="Filter by integration type")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    health_status: Optional[HealthStatus] = Field(None, description="Filter by health status")
    sync_status: Optional[SyncStatus] = Field(None, description="Filter by sync status")
    organization_id: Optional[uuid.UUID] = Field(None, description="Filter by organization")
    created_after: Optional[datetime] = Field(None, description="Filter by creation date")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date")
    sort_by: Optional[str] = Field("created_at", description="Sort field")
    sort_order: Optional[str] = Field("desc", description="Sort order: asc or desc")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v not in ['asc', 'desc']:
            raise ValueError('Sort order must be "asc" or "desc"')
        return v
    
    class Config:
        json_encoders = {
            uuid.UUID: str,
            datetime: lambda v: v.isoformat()
        }


class IntegrationLog(BaseModel):
    """Schema for integration activity logs"""
    id: uuid.UUID
    integration_id: uuid.UUID
    action: str
    status: str
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    duration: Optional[float] = None  # in seconds
    created_at: datetime
    created_by: Optional[uuid.UUID] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            uuid.UUID: str,
            datetime: lambda v: v.isoformat()
        }


class IntegrationLogListResponse(BaseModel):
    """Schema for paginated integration logs"""
    logs: List[IntegrationLog]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool