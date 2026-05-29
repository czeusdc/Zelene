"""Module: SQLAlchemy ORM models for the Zelene intelligence platform.

This module defines the complete database schema including company profiles,
user settings, deployments, signals, entities, relationships, insights,
messages, and embedding tables for vector search.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from src.db.base import Base


def utcnow():
    """Return the current UTC datetime, used as a default for timestamp columns."""
    return datetime.now(timezone.utc)


class CompanyProfile(Base):
    """A company profile captured during onboarding."""
    __tablename__ = "company_profiles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    industry = Column(String(255))
    description = Column(Text)
    competitors = Column(ARRAY(String))
    market_focus = Column(ARRAY(String))
    business_goals = Column(ARRAY(String))
    operational_concerns = Column(ARRAY(String))
    created_at = Column(DateTime(timezone=True), default=utcnow)
    settings = relationship("UserSettings", back_populates="company", uselist=False, cascade="all, delete-orphan")
    deployments = relationship("Deployment", back_populates="company", cascade="all, delete-orphan")

class UserSettings(Base):
    """Per-company user preferences including model selection.

    API keys are NEVER stored in the database — they are read from
    environment variables (.env) for server-side use or validated
    per-session for user-provided keys.
    """

    __tablename__ = "user_settings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company_profiles.id", ondelete="CASCADE"), unique=True)
    llm_model = Column(String(50), default="deepseek/deepseek-v4-pro")
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    company = relationship("CompanyProfile", back_populates="settings")

class Deployment(Base):
    """An intelligence-gathering deployment run for a company."""

    __tablename__ = "deployments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company_profiles.id", ondelete="CASCADE"))
    mode = Column(String(20), default="auto")
    status = Column(String(20), default="pending")
    signals_found = Column(Integer, default=0)
    relationships_mapped = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True), default=utcnow)
    completed_at = Column(DateTime(timezone=True))
    company = relationship("CompanyProfile", back_populates="deployments")
    signals = relationship("Signal", back_populates="deployment", cascade="all, delete-orphan")

class Signal(Base):
    """An intelligence signal discovered during a deployment."""

    __tablename__ = "signals"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deployment_id = Column(UUID(as_uuid=True), ForeignKey("deployments.id", ondelete="CASCADE"))
    company_id = Column(UUID(as_uuid=True), ForeignKey("company_profiles.id", ondelete="CASCADE"))
    signal_type = Column("type", String(50), nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(500), nullable=False)
    source_url = Column(String(1000))
    confidence = Column(Float, default=0.0)
    severity = Column(String(20), default="info")
    entities = Column(ARRAY(String))
    conflicts_with = Column(ARRAY(UUID))
    extracted_at = Column(DateTime(timezone=True), default=utcnow)
    deployment = relationship("Deployment", back_populates="signals")

class Entity(Base):
    """A named entity (person, organization, location, etc.) extracted from signals."""

    __tablename__ = "entities"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company_profiles.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    entity_type = Column("type", String(50), nullable=False)
    description = Column(Text)
    activity_level = Column(Float, default=0.0)
    last_signal_at = Column(DateTime(timezone=True))

class Relationship(Base):
    """A relationship link between two entities discovered during analysis."""

    __tablename__ = "relationships"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deployment_id = Column(UUID(as_uuid=True), ForeignKey("deployments.id", ondelete="CASCADE"))
    entity_a = Column(UUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE"))
    entity_b = Column(UUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE"))
    relationship_type = Column(String(50), nullable=False)
    strength = Column(Float, default=0.5)
    evidence = Column(ARRAY(String))
    created_at = Column(DateTime(timezone=True), default=utcnow)

class Insight(Base):
    """A synthesized insight generated from related signals."""

    __tablename__ = "insights"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deployment_id = Column(UUID(as_uuid=True), ForeignKey("deployments.id", ondelete="CASCADE"))
    company_id = Column(UUID(as_uuid=True), ForeignKey("company_profiles.id", ondelete="CASCADE"))
    insight_type = Column("type", String(50), nullable=False)
    title = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    reasoning = Column(Text)
    confidence = Column(Float, default=0.0)
    evidence_signals = Column(ARRAY(UUID))
    actions = Column(ARRAY(String))
    dismissed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

class Message(Base):
    """A chat message exchanged in a conversational session."""

    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company_profiles.id", ondelete="CASCADE"))
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    related_insight = Column(UUID(as_uuid=True), ForeignKey("insights.id"))
    created_at = Column(DateTime(timezone=True), default=utcnow)

class SignalEmbedding(Base):
    """Vector embedding of a signal's content for semantic search."""

    __tablename__ = "signal_embeddings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    signal_id = Column(UUID(as_uuid=True), ForeignKey("signals.id", ondelete="CASCADE"))
    embedding = Column(Vector(768))
    created_at = Column(DateTime(timezone=True), default=utcnow)

class CompanyContextEmbedding(Base):
    """Vector embedding of company context content for semantic matching."""

    __tablename__ = "company_context_embeddings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company_profiles.id", ondelete="CASCADE"))
    embedding = Column(Vector(768))
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), default=utcnow)
