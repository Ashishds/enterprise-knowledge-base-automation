"""
SQLAlchemy ORM Models.

Defines all 10 required database tables (docs/ARCHITECTURE.md §4.1):
  1. tenants
  2. users
  3. documents
  4. ingestion_jobs
  5. conversations
  6. messages
  7. request_usage
  8. user_feedback
  9. prompt_releases
 10. audit_events (append-only)
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    ARRAY,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def utc_now() -> datetime:
    return datetime.now(UTC)


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    status = Column(String(32), nullable=False, default="active")
    settings_json = Column(JSONB, nullable=False, default=dict)
    kb_version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)


class User(Base):
    __tablename__ = "users"

    id = Column(String(128), primary_key=True)  # Cognito sub
    tenant_id = Column(
        String(64), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    email = Column(String(255), nullable=False)
    role = Column(String(32), nullable=False, default="user")
    departments = Column(ARRAY(String), nullable=False, default=list)
    status = Column(String(32), nullable=False, default="active")
    last_login_at = Column(DateTime(timezone=True), nullable=True)


class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(
        String(64), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    department = Column(String(64), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    s3_uri = Column(Text, nullable=False)
    mime_type = Column(String(128), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    checksum = Column(String(64), nullable=False, index=True)
    version = Column(Integer, nullable=False, default=1)
    owner_id = Column(String(128), nullable=False)
    status = Column(String(32), nullable=False, default="active")  # active | retired
    page_count = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    retired_at = Column(DateTime(timezone=True), nullable=True)


class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(64), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(String(64), nullable=False, index=True)
    state = Column(
        String(32), nullable=False, default="queued"
    )  # queued | processing | completed | failed
    stage = Column(String(64), nullable=False, default="initiated")
    attempts = Column(Integer, nullable=False, default=0)
    error_code = Column(String(64), nullable=True)
    error_detail = Column(Text, nullable=True)
    chunks_written = Column(Integer, nullable=False, default=0)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    user_id = Column(String(128), nullable=False, index=True)
    title = Column(String(255), nullable=False, default="New Conversation")
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    last_message_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)


class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(
        String(64), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role = Column(String(32), nullable=False)  # user | assistant | system
    content = Column(Text, nullable=False)
    citations_json = Column(JSONB, nullable=False, default=list)
    trace_id = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)


class RequestUsage(Base):
    __tablename__ = "request_usage"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    user_id = Column(String(128), nullable=False, index=True)
    route = Column(String(128), nullable=False)
    model = Column(String(64), nullable=False)
    input_tokens = Column(BigInteger, nullable=False, default=0)
    output_tokens = Column(BigInteger, nullable=False, default=0)
    estimated_cost = Column(Numeric(10, 6), nullable=False, default=0.0)
    latency_ms = Column(Integer, nullable=False, default=0)
    cache_status = Column(String(32), nullable=False, default="miss")
    route_selected = Column(String(64), nullable=False, default="default")
    fallback_used = Column(Boolean, nullable=False, default=False)
    prompt_version = Column(String(32), nullable=False, default="1.0.0")
    trace_id = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)


class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String(64), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(128), nullable=False)
    tenant_id = Column(String(64), nullable=False, index=True)
    rating = Column(Integer, nullable=False)  # 1-5 or -1/+1
    reason = Column(String(128), nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)


class PromptRelease(Base):
    __tablename__ = "prompt_releases"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(128), nullable=False)
    version = Column(String(32), nullable=False)
    template = Column(Text, nullable=False)
    checksum = Column(String(64), nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    released_by = Column(String(128), nullable=False)
    released_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)


class AuditEvent(Base):
    """Append-only audit log table."""

    __tablename__ = "audit_events"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    actor_id = Column(String(128), nullable=False, index=True)
    action = Column(String(128), nullable=False)
    resource_type = Column(String(64), nullable=False)
    resource_id = Column(String(128), nullable=False)
    outcome = Column(String(32), nullable=False)  # success | denied | failed
    correlation_id = Column(String(64), nullable=False, index=True)
    ip = Column(String(45), nullable=True)
    metadata_json = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
