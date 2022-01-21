"""Set nullability for all columns

Revision ID: 98124b2b5559
Revises: a30dccf9af29
Create Date: 2022-01-14 22:33:59.880685

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '98124b2b5559'
down_revision = 'a30dccf9af29'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('file', schema=None) as batch_op:
        batch_op.alter_column('url',
               existing_type=sa.TEXT(),
               nullable=False)
        batch_op.alter_column('uploader_id',
               existing_type=sa.NUMERIC(precision=16),
               nullable=False)
        batch_op.alter_column('created_at',
               existing_type=sa.DATETIME(),
               nullable=False)

    with op.batch_alter_table('route', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=150),
               nullable=False)
        batch_op.alter_column('category',
               existing_type=sa.VARCHAR(length=12),
               nullable=False)
        batch_op.alter_column('mark_color',
               existing_type=sa.VARCHAR(length=150),
               nullable=False)
        batch_op.alter_column('author',
               existing_type=sa.VARCHAR(length=150),
               nullable=False)
        batch_op.alter_column('uploader_id',
               existing_type=sa.NUMERIC(precision=16),
               nullable=False)
        batch_op.alter_column('description',
               existing_type=sa.VARCHAR(length=2000),
               nullable=False)
        batch_op.alter_column('creation_date',
               existing_type=sa.DATE(),
               nullable=False)

    with op.batch_alter_table('routeimage', schema=None) as batch_op:
        batch_op.alter_column('route_id',
               existing_type=sa.NUMERIC(precision=16),
               nullable=False)
        batch_op.alter_column('image_id',
               existing_type=sa.NUMERIC(precision=16),
               nullable=False)

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('username',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
        batch_op.alter_column('first_name',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
        batch_op.alter_column('last_name',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('last_name',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
        batch_op.alter_column('first_name',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
        batch_op.alter_column('username',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)

    with op.batch_alter_table('routeimage', schema=None) as batch_op:
        batch_op.alter_column('image_id',
               existing_type=sa.NUMERIC(precision=16),
               nullable=True)
        batch_op.alter_column('route_id',
               existing_type=sa.NUMERIC(precision=16),
               nullable=True)

    with op.batch_alter_table('route', schema=None) as batch_op:
        batch_op.alter_column('creation_date',
               existing_type=sa.DATE(),
               nullable=True)
        batch_op.alter_column('description',
               existing_type=sa.VARCHAR(length=2000),
               nullable=True)
        batch_op.alter_column('uploader_id',
               existing_type=sa.NUMERIC(precision=16),
               nullable=True)
        batch_op.alter_column('author',
               existing_type=sa.VARCHAR(length=150),
               nullable=True)
        batch_op.alter_column('mark_color',
               existing_type=sa.VARCHAR(length=150),
               nullable=True)
        batch_op.alter_column('category',
               existing_type=sa.VARCHAR(length=12),
               nullable=True)
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=150),
               nullable=True)

    with op.batch_alter_table('file', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=sa.DATETIME(),
               nullable=True)
        batch_op.alter_column('uploader_id',
               existing_type=sa.NUMERIC(precision=16),
               nullable=True)
        batch_op.alter_column('url',
               existing_type=sa.TEXT(),
               nullable=True)

    # ### end Alembic commands ###