"""Add ONDELETE=CASCADE in acess_token_table

Revision ID: 8a70bb7f92fb
Revises: d931930fbfbe
Create Date: 2023-10-17 00:49:01.385311

"""

import fastapi_users_db_sqlmodel
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "8a70bb7f92fb"
down_revision = "d931930fbfbe"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("accesstoken", schema=None) as batch_op:
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DATETIME(),
            type_=fastapi_users_db_sqlmodel.generics.TIMESTAMPAware(
                timezone=True
            ),
            existing_nullable=False,
        )
        meta = sa.MetaData()
        meta.reflect(bind=batch_op.get_bind(), only=("accesstoken",))
        accesstoken = sa.Table("accesstoken", meta)
        constraints = list(
            filter(
                lambda c: isinstance(c, sa.ForeignKeyConstraint),
                list(accesstoken.constraints),
            )
        )
        if len(constraints) != 1:
            raise KeyError(
                f"Found {len(constraints)} fk constraints in accesstoken table"
            )
        batch_op.drop_constraint(constraints[0], type_="foreignkey")
        batch_op.create_foreign_key(
            "accesstoken_user_fk",
            "user",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )

    with op.batch_alter_table("oauthaccount", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_oauthaccount_account_id"),
            ["account_id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_oauthaccount_oauth_name"),
            ["oauth_name"],
            unique=False,
        )
        meta = sa.MetaData()
        meta.reflect(bind=batch_op.get_bind(), only=("oauthaccount",))
        oauthaccount = sa.Table("oauthaccount", meta)
        constraints = list(
            filter(
                lambda c: isinstance(c, sa.ForeignKeyConstraint),
                list(oauthaccount.constraints),
            )
        )
        if len(constraints) != 1:
            raise KeyError(
                f"Found {len(constraints)} fk constraints in oauthaccount table"
            )
        batch_op.drop_constraint(constraints[0], type_="foreignkey")
        batch_op.create_foreign_key(
            "oauthaccount_user_fk",
            "user",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("oauthaccount", schema=None) as batch_op:
        batch_op.drop_constraint("oauthaccount_user_fk", type_="foreignkey")
        batch_op.create_foreign_key(None, "user", ["user_id"], ["id"])
        batch_op.drop_index(batch_op.f("ix_oauthaccount_oauth_name"))
        batch_op.drop_index(batch_op.f("ix_oauthaccount_account_id"))

    with op.batch_alter_table("accesstoken", schema=None) as batch_op:
        batch_op.drop_constraint("accesstoken_user_fk", type_="foreignkey")
        batch_op.create_foreign_key(None, "user", ["user_id"], ["id"])
        batch_op.alter_column(
            "created_at",
            existing_type=fastapi_users_db_sqlmodel.generics.TIMESTAMPAware(
                timezone=True
            ),
            type_=sa.DATETIME(),
            existing_nullable=False,
        )

    # ### end Alembic commands ###
