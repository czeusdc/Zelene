"""add_indexes_and_limits

Revision ID: 378ed7ca734f
Revises: 63c240e2f13b
Create Date: 2026-05-27 06:57:14.996502

Adds indexes on foreign keys for query performance and sets VARCHAR limits
on text-heavy columns to prevent unbounded storage growth on Neon free tier.
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "378ed7ca734f"
down_revision: Union[str, Sequence[str], None] = "63c240e2f13b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add performance indexes and column constraints."""
    op.create_index("ix_signals_deployment_id", "signals", ["deployment_id"])
    op.create_index("ix_signals_company_extracted", "signals", ["company_id", sa.text("extracted_at DESC")])
    op.create_index("ix_entities_company_id", "entities", ["company_id"])
    op.create_index("ix_relationships_deployment_id", "relationships", ["deployment_id"])
    op.create_index("ix_insights_deployment_id", "insights", ["deployment_id"])
    op.create_index("ix_messages_company_created", "messages", ["company_id", sa.text("created_at DESC")])
    op.create_index("ix_deployments_company_started", "deployments", ["company_id", sa.text("started_at DESC")])

    # Cap unbounded Text columns at 10,000 characters for space control
    op.alter_column("signals", "content", type_=sa.String(10000), existing_type=sa.Text())
    op.alter_column("signals", "source_url", type_=sa.String(2000), existing_type=sa.String(1000))
    op.alter_column("insights", "body", type_=sa.String(10000), existing_type=sa.Text())
    op.alter_column("insights", "reasoning", type_=sa.String(5000), existing_type=sa.Text())
    op.alter_column("messages", "content", type_=sa.String(10000), existing_type=sa.Text())


def downgrade() -> None:
    """Revert to unbounded text columns and drop indexes."""
    op.alter_column("messages", "content", type_=sa.Text(), existing_type=sa.String(10000))
    op.alter_column("insights", "reasoning", type_=sa.Text(), existing_type=sa.String(5000))
    op.alter_column("insights", "body", type_=sa.Text(), existing_type=sa.String(10000))
    op.alter_column("signals", "source_url", type_=sa.String(1000), existing_type=sa.String(2000))
    op.alter_column("signals", "content", type_=sa.Text(), existing_type=sa.String(10000))

    op.drop_index("ix_deployments_company_started")
    op.drop_index("ix_messages_company_created")
    op.drop_index("ix_insights_deployment_id")
    op.drop_index("ix_relationships_deployment_id")
    op.drop_index("ix_entities_company_id")
    op.drop_index("ix_signals_company_extracted")
    op.drop_index("ix_signals_deployment_id")
