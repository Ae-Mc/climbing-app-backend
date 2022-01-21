"""First test revision

Revision ID: 8ab8aaacbb9b
Revises: 
Create Date: 2022-01-14 17:03:21.854001

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
import fastapi_users_db_sqlalchemy


# revision identifiers, used by Alembic.
revision = '8ab8aaacbb9b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', fastapi_users_db_sqlalchemy.guid.GUID(), nullable=False),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('hashed_password', sa.String(length=72), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=True),
    sa.Column('first_name', sa.String(length=100), nullable=True),
    sa.Column('last_name', sa.String(length=100), nullable=True),
    sa.Column('creation_date', sa.Date(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('file',
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
    sa.Column('url', sa.Text(), nullable=True),
    sa.Column('uploader_id', fastapi_users_db_sqlalchemy.guid.GUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['uploader_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_file_id'), 'file', ['id'], unique=False)
    op.create_table('route',
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
    sa.Column('name', sa.String(length=150), nullable=True),
    sa.Column('category', sa.Enum('FIVE_A', 'FIVE_A_PLUS', 'FIVE_B', 'FIVE_B_PLUS', 'FIVE_C', 'FIVE_C_PLUS', 'SIX_A', 'SIX_A_PLUS', 'SIX_B', 'SIX_B_PLUS', 'SIX_C', 'SIX_C_PLUS', 'SEVEN_A', 'SEVEN_A_PLUS', 'SEVEN_B', 'SEVEN_B_PLUS', 'SEVEN_C', 'SEVEN_C_PLUS', 'EIGHT_A', 'EIGHT_A_PLUS', 'EIGHT_B', 'EIGHT_B_PLUS', 'EIGHT_C', 'EIGHT_C_PLUS', 'NINE_A', 'NINE_A_PLUS', 'NINE_B', 'NINE_B_PLUS', 'NINE_C', 'NINE_C_PLUS', name='category'), nullable=True),
    sa.Column('mark_color', sa.String(length=150), nullable=True),
    sa.Column('author', sa.String(length=150), nullable=True),
    sa.Column('uploader_id', fastapi_users_db_sqlalchemy.guid.GUID(), nullable=True),
    sa.Column('description', sa.String(length=2000), nullable=True),
    sa.Column('creation_date', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['uploader_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_route_id'), 'route', ['id'], unique=False)
    op.create_table('routeimage',
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
    sa.Column('route_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=True),
    sa.Column('image_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=True),
    sa.ForeignKeyConstraint(['image_id'], ['file.id'], ),
    sa.ForeignKeyConstraint(['route_id'], ['route.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('routeimage')
    op.drop_index(op.f('ix_route_id'), table_name='route')
    op.drop_table('route')
    op.drop_index(op.f('ix_file_id'), table_name='file')
    op.drop_table('file')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###