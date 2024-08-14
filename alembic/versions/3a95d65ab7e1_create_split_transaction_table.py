"""create split transaction table

Revision ID: 3a95d65ab7e1
Revises: 616e66ae7df2
Create Date: 2023-10-13 19:02:08.507080

"""
from alembic import op
from sqlalchemy import FLOAT
from sqlalchemy import TEXT, Column, DateTime, INTEGER, ForeignKey
from sqlalchemy.engine.reflection import Inspector

from balance_api.data.models import SplitTransaction


# revision identifiers, used by Alembic.
revision = "3a95d65ab7e1"
down_revision = "616e66ae7df2"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()
    if SplitTransaction.__tablename__ not in tables:
        op.create_table(
            SplitTransaction.__tablename__,
            Column("id", INTEGER, primary_key=True, autoincrement=True),
            Column(
                "transaction_id",
                INTEGER,
                ForeignKey("transactions.id", onupdate="CASCADE", ondelete="CASCADE"),
            ),
            Column("amount", FLOAT),
            Column("description", TEXT),
            Column("tag_id", INTEGER, ForeignKey("tags.id", onupdate="CASCADE")),
            Column("created_at", DateTime, nullable=False),
            Column("updated_at", DateTime, nullable=False),
        )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table(SplitTransaction.__tablename__)
    # ### end Alembic commands ###
