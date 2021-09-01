"""Create transaction asset table

Revision ID: a8c0c8235c5f
Revises: a4c1e7240a0c
Create Date: 2021-07-05 16:57:19.395615

"""
from alembic import op
from sqlalchemy import TEXT, Column, ForeignKey, DateTime, INTEGER
from sqlalchemy.engine.reflection import Inspector

from balance_api.models.transaction_asset import TransactionAsset

# revision identifiers, used by Alembic.
revision = "a8c0c8235c5f"
down_revision = "a4c1e7240a0c"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()
    if TransactionAsset.__tablename__ not in tables:
        op.create_table(
            TransactionAsset.__tablename__,
            Column(
                "transaction_id",
                INTEGER,
                ForeignKey("transactions.id", onupdate="CASCADE", ondelete="CASCADE"),
            ),
            Column(
                "asset_isin",
                TEXT,
                ForeignKey("assets.isin", onupdate="CASCADE", ondelete="CASCADE"),
            ),
            Column("created_at", DateTime, nullable=False),
            Column("updated_at", DateTime, nullable=False),
        )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table(TransactionAsset.__tablename__)
    # ### end Alembic commands ###
