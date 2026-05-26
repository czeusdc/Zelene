import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from src.db.base import Base

def utcnow():
    return datetime.now(timezone.utc)

class CompanyProfile(Base):
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
    __tablename__ = "user_settings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company_profiles.id", ondelete="CASCADE"), unique=True)
    gemini_api_key = Column(Text)
    gemini_model = Column(String(50), default="gemini-3.1-pro")
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    company = relationship("CompanyProfile", back_populates="settings")

class Deployment(Base):
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
    __tablename__ = "signals"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deployment_id = Column(UUID(as_uuid=True), ForeignKey("deployments.id", ondelete="CASCADE"))
    company_id = Column(UUID(as_uuid=True), ForeignKey("company_profiles.id", ondelete="CASCADE"))
    type = Column(String(50), nullable=False)
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
    __tablename__ = "entities"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company_profiles.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    description = Column(Text)
    activity_level = Column(Float, default=0.0)
    last_signal_at = Column(DateTime(timezone=True))

class Relationship(Base):
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
    __tablename__ = "insights"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deployment_id = Column(UUID(as_uuid=True), ForeignKey("deployments.id", ondelete="CASCADE"))
    company_id = Column(UUID(as_uuid=True), ForeignKey("company_profiles.id", ondelete="CASCADE"))
    type = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    reasoning = Column(Text)
    confidence = Column(Float, default=0.0)
    evidence_signals = Column(ARRAY(UUID))
    actions = Column(ARRAY(String))
    dismissed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

class Message(Base):
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company_profiles.id", ondelete="CASCADE"))
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    related_insight = Column(UUID(as_uuid=True), ForeignKey("insights.id"))
    created_at = Column(DateTime(timezone=True), default=utcnow)

class SignalEmbedding(Base):
    __tablename__ = "signal_embeddings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    signal_id = Column(UUID(as_uuid=True), ForeignKey("signals.id", ondelete="CASCADE"))
    embedding = Column(Vector(768))
    created_at = Column(DateTime(timezone=True), default=utcnow)

class CompanyContextEmbedding(Base):
    __tablename__ = "company_context_embeddings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company_profiles.id", ondelete="CASCADE"))
    embedding = Column(Vector(768))
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), default=utcnow)
