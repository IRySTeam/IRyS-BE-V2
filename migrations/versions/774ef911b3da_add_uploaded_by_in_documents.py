"""add uploaded by in documents

Revision ID: 774ef911b3da
Revises: 70363c29098f
Create Date: 2023-05-01 16:43:35.324132

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "774ef911b3da"
down_revision = "70363c29098f"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("documents", sa.Column("uploaded_by", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "documents_uploaded_by_fkey",
        "documents",
        "users",
        ["uploaded_by"],
        ["id"],
        ondelete="CASCADE",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("documents_uploaded_by_fkey", "documents", type_="foreignkey")
    op.drop_column("documents", "uploaded_by")
    # ### end Alembic commands ###
