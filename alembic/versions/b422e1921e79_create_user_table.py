"""Create user table

Revision ID: b422e1921e79
Revises:
Create Date: 2021-06-20 16:09:36.223360

"""
from alembic import op
from sqlalchemy import TEXT, Column, INTEGER, DateTime
from sqlalchemy.engine.reflection import Inspector

from balance_api.models.users import User

# revision identifiers, used by Alembic.
revision = 'b422e1921e79'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()
    if User.__tablename__ not in tables:
        op.create_table(
            User.__tablename__,
            Column("id", INTEGER, primary_key=True, autoincrement=True),
            Column("name", TEXT),
            Column("email", TEXT),
            Column("created_at", DateTime, nullable=False),
            Column("updated_at", DateTime, nullable=False),
        )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table(User.__tablename__)
    # ### end Alembic commands ###
