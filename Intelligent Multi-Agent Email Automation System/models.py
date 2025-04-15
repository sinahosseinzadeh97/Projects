"""
Data models for the Intelligent Multi-Agent Email Automation System.
This file defines Pydantic models for API requests and responses.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum

# Email Provider Models
class ProviderType(str, Enum):
    GMAIL = "gmail"
    OUTLOOK = "outlook"
    IMAP = "imap"
    EXCHANGE = "exchange"
    OTHER = "other"

class EmailProviderBase(BaseModel):
    type: ProviderType
    server: str
    username: str
    folder: str = "INBOX"
    limit: int = 10

class EmailProviderCreate(EmailProviderBase):
    password: str

class EmailProvider(EmailProviderBase):
    id: str
    created_at: datetime
    
    class Config:
        orm_mode = True

# Email Models
class EmailAttachment(BaseModel):
    filename: str
    content_type: str
    size: int

class EmailBase(BaseModel):
    message_id: str
    subject: str
    from_address: str = Field(..., alias="from")
    to: str
    cc: Optional[str] = None
    body: str
    attachments: List[EmailAttachment] = []

class Email(EmailBase):
    id: str
    provider_id: str
    timestamp: datetime
    
    class Config:
        orm_mode = True

# Classification Models
class CategoryProbability(BaseModel):
    category: str
    probability: float

class Classification(BaseModel):
    message_id: str
    predicted_category: str
    confidence: float
    category_probabilities: Dict[str, float]

class ClassifiedEmail(Email):
    classification: Classification

# Extraction Models
class ExtractedItem(BaseModel):
    text: str
    type: str

class Extractions(BaseModel):
    dates_times: List[ExtractedItem] = []
    contacts: List[ExtractedItem] = []
    tasks: List[ExtractedItem] = []

class ProcessedData(BaseModel):
    message_id: str
    summary: str
    extractions: Extractions
    processing_timestamp: datetime

class ProcessedEmail(ClassifiedEmail):
    processed_data: ProcessedData

# Response Models
class ResponseData(BaseModel):
    message_id: str
    response_text: str
    auto_send: bool
    confidence: float
    category: str
    generation_timestamp: datetime
    sent: Optional[bool] = None
    sent_timestamp: Optional[datetime] = None

class EmailWithResponse(ProcessedEmail):
    response_data: ResponseData

# Integration Models
class CalendarEvent(BaseModel):
    title: str
    datetime: str
    description: Optional[str] = None
    attendees: List[str] = []
    location: Optional[str] = None
    duration_minutes: int = 60

class CalendarIntegrationResult(BaseModel):
    service: str
    events_created: List[Dict[str, Any]]
    status: str
    timestamp: datetime

class CrmContact(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None

class CrmIntegrationResult(BaseModel):
    service: str
    contacts_updated: List[Dict[str, Any]]
    status: str
    timestamp: datetime

class Task(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: str = "medium"
    assignee: Optional[str] = None

class TaskIntegrationResult(BaseModel):
    service: str
    tasks_created: List[Dict[str, Any]]
    status: str
    timestamp: datetime

class IntegrationResults(BaseModel):
    calendar: Optional[CalendarIntegrationResult] = None
    crm: Optional[CrmIntegrationResult] = None
    task_manager: Optional[TaskIntegrationResult] = None

class EmailWithIntegrations(EmailWithResponse):
    integrations: Optional[IntegrationResults] = None

# Workflow Models
class WorkflowResult(BaseModel):
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    emails_processed: int
    emails_with_responses: int
    emails_auto_sent: int
    emails_with_calendar_integration: int
    emails_with_crm_integration: int
    emails_with_task_integration: int
    status: str
    error: Optional[str] = None

# Configuration Models
class DatabaseConfig(BaseModel):
    mongodb_url: str
    database_name: str

class CacheConfig(BaseModel):
    redis_host: str
    redis_port: int
    redis_db: int

class ApiConfig(BaseModel):
    host: str
    port: int
    debug: bool
    cors_origins: List[str]

class EmailIngestionConfig(BaseModel):
    batch_size: int
    polling_interval: int

class ClassificationConfig(BaseModel):
    model_type: str
    categories: List[str]
    threshold: float

class SummarizationConfig(BaseModel):
    model_type: str
    summary_max_length: int

class ResponseGenerationConfig(BaseModel):
    model_type: str
    auto_send_threshold: float
    templates: Dict[str, str]

class WorkflowConfig(BaseModel):
    auto_send_enabled: bool
    batch_size: int

class IntegrationServiceConfig(BaseModel):
    enabled: bool
    service: str

class IntegrationsConfig(BaseModel):
    calendar: IntegrationServiceConfig
    crm: IntegrationServiceConfig
    task_manager: IntegrationServiceConfig

class IntegrationConfig(BaseModel):
    workflow: WorkflowConfig
    integrations: IntegrationsConfig

class LoggingConfig(BaseModel):
    level: str
    file: str
    max_size: int
    backup_count: int

class SystemConfig(BaseModel):
    database: DatabaseConfig
    cache: CacheConfig
    api: ApiConfig
    email_ingestion: EmailIngestionConfig
    classification: ClassificationConfig
    summarization: SummarizationConfig
    response_generation: ResponseGenerationConfig
    integration: IntegrationConfig
    logging: LoggingConfig
"""
