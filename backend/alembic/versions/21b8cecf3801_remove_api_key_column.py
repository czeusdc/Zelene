"""remove_api_key_column

Revision ID: 21b8cecf3801
Revises: 378ed7ca734f
Create Date: 2026-05-27 07:17:11.376066

Removes gemini_api_key from user_settings. API keys must never be stored in
the database — they live in .env environment variables exclusively.
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "21b8cecf3801"
down_revision: Union[str, Sequence[str], None] = "378ed7ca734f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("user_settings", "gemini_api_key")


def downgrade() -> None:
    op.add_column("user_settings", sa.Column("gemini_api_key", sa.Text(), nullable=True))
