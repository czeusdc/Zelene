"""initial_schema

Revision ID: 63c240e2f13b
Revises: 
Create Date: 2026-05-27 02:23:58.365476

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '63c240e2f13b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "company_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("industry", sa.String(255)),
        sa.Column("description", sa.Text()),
        sa.Column("competitors", postgresql.ARRAY(sa.String())),
        sa.Column("market_focus", postgresql.ARRAY(sa.String())),
        sa.Column("business_goals", postgresql.ARRAY(sa.String())),
        sa.Column("operational_concerns", postgresql.ARRAY(sa.String())),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "user_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("company_profiles.id", ondelete="CASCADE"), unique=True),
        sa.Column("gemini_api_key", sa.Text()),
        sa.Column("gemini_model", sa.String(50), server_default="gemini-3.1-pro"),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "deployments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("company_profiles.id", ondelete="CASCADE")),
        sa.Column("mode", sa.String(20), server_default="auto"),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("signals_found", sa.Integer(), server_default="0"),
        sa.Column("relationships_mapped", sa.Integer(), server_default="0"),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "signals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("deployment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("deployments.id", ondelete="CASCADE")),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("company_profiles.id", ondelete="CASCADE")),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source", sa.String(500), nullable=False),
        sa.Column("source_url", sa.String(1000)),
        sa.Column("confidence", sa.Float(), server_default="0.0"),
        sa.Column("severity", sa.String(20), server_default="info"),
        sa.Column("entities", postgresql.ARRAY(sa.String())),
        sa.Column("conflicts_with", postgresql.ARRAY(postgresql.UUID())),
        sa.Column("extracted_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "entities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("company_profiles.id", ondelete="CASCADE")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("activity_level", sa.Float(), server_default="0.0"),
        sa.Column("last_signal_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "relationships",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("deployment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("deployments.id", ondelete="CASCADE")),
        sa.Column("entity_a", postgresql.UUID(as_uuid=True), sa.ForeignKey("entities.id", ondelete="CASCADE")),
        sa.Column("entity_b", postgresql.UUID(as_uuid=True), sa.ForeignKey("entities.id", ondelete="CASCADE")),
        sa.Column("relationship_type", sa.String(50), nullable=False),
        sa.Column("strength", sa.Float(), server_default="0.5"),
        sa.Column("evidence", postgresql.ARRAY(sa.String())),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "insights",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("deployment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("deployments.id", ondelete="CASCADE")),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("company_profiles.id", ondelete="CASCADE")),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("reasoning", sa.Text()),
        sa.Column("confidence", sa.Float(), server_default="0.0"),
        sa.Column("evidence_signals", postgresql.ARRAY(postgresql.UUID())),
        sa.Column("actions", postgresql.ARRAY(sa.String())),
        sa.Column("dismissed", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("company_profiles.id", ondelete="CASCADE")),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("related_insight", postgresql.UUID(as_uuid=True), sa.ForeignKey("insights.id")),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "signal_embeddings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("signal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("signals.id", ondelete="CASCADE")),
        sa.Column("embedding", postgresql.VECTOR(768)),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "company_context_embeddings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("company_profiles.id", ondelete="CASCADE")),
        sa.Column("embedding", postgresql.VECTOR(768)),
        sa.Column("content", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )


def downgrade() -> None:
    op.drop_table("company_context_embeddings")
    op.drop_table("signal_embeddings")
    op.drop_table("messages")
    op.drop_table("insights")
    op.drop_table("relationships")
    op.drop_table("entities")
    op.drop_table("signals")
    op.drop_table("deployments")
    op.drop_table("user_settings")
    op.drop_table("company_profiles")
    op.execute("DROP EXTENSION IF EXISTS vector")
