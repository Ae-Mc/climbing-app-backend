"""Add opt-in tourist marker. Existing users are ordinary users.

Revision ID: 62c5e0a9b441
Revises: ede4ba9c2dfe
"""
from alembic import op
import sqlalchemy as sa

revision = "62c5e0a9b441"
down_revision = "ede4ba9c2dfe"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("user", sa.Column("is_tourist", sa.Boolean(), nullable=False, server_default=sa.text("0")))

def downgrade():
    op.drop_column("user", "is_tourist")
