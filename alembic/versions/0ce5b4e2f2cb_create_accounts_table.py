"""Create accounts table

Revision ID: 0ce5b4e2f2cb
Revises: b422e1921e79
Create Date: 2021-06-20 16:28:15.958831

"""

from alembic import op
from sqlalchemy import TEXT, Column, INTEGER, ForeignKey, Enum, DateTime
from sqlalchemy.engine.reflection import Inspector

from balance_api.data.models.accounts import Account, AccountType

# revision identifiers, used by Alembic.
revision = "0ce5b4e2f2cb"
down_revision = "b422e1921e79"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()
    if Account.__tablename__ not in tables:
        op.create_table(
            Account.__tablename__,
            Column("id", INTEGER, primary_key=True, autoincrement=True),
            Column("alias", TEXT),
            Column(
                "user_id",
                INTEGER,
                ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
            ),
            Column("type", Enum(AccountType), nullable=False),
            Column("created_at", DateTime, nullable=False),
            Column("updated_at", DateTime, nullable=False),
        )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table(Account.__tablename__)
    # ### end Alembic commands ###
