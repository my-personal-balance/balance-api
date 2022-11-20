"""create account mappers

Revision ID: 616e66ae7df2
Revises: d964d0ccd9c6
Create Date: 2022-01-09 11:20:54.483454

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.engine.reflection import Inspector

from balance_api.models.account_mappers import AccountMapper, SourceFileType

# revision identifiers, used by Alembic.
revision = "616e66ae7df2"
down_revision = "d964d0ccd9c6"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()

    if AccountMapper.__tablename__ not in tables:
        op.create_table(
            AccountMapper.__tablename__,
            sa.Column("id", sa.INTEGER, primary_key=True, autoincrement=True),
            sa.Column(
                "account_id",
                sa.INTEGER,
                sa.ForeignKey("accounts.id", onupdate="CASCADE", ondelete="CASCADE"),
            ),
            sa.Column("source_file_type", sa.Enum(SourceFileType), nullable=False),
            sa.Column("source_file_schema", sa.JSON, nullable=False),
            sa.Column("created_at", sa.DateTime, nullable=False),
            sa.Column("updated_at", sa.DateTime, nullable=False),
        )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table(AccountMapper.__tablename__)
    # ### end Alembic commands ###
