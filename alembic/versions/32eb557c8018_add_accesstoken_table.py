"""Add AccessToken table

Revision ID: 32eb557c8018
Revises: 98124b2b5559
Create Date: 2022-01-15 21:56:41.055649

"""
from alembic import op
import sqlalchemy as sa
import fastapi_users_db_sqlalchemy
import sqlalchemy_utils

# revision identifiers, used by Alembic.
revision = '32eb557c8018'
down_revision = '98124b2b5559'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('accesstoken',
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
    sa.Column('token', sa.String(length=43), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('user_id', fastapi_users_db_sqlalchemy.guid.GUID(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='cascade'),
    sa.PrimaryKeyConstraint('id', 'token')
    )
    with op.batch_alter_table('accesstoken', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_accesstoken_created_at'), ['created_at'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('accesstoken', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_accesstoken_created_at'))

    op.drop_table('accesstoken')
    # ### end Alembic commands ###