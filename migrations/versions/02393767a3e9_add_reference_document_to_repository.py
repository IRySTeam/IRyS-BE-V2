"""Add reference document to repository

Revision ID: 02393767a3e9
Revises: 5f1f5bc6b44e
Create Date: 2023-04-22 19:38:57.405668

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "02393767a3e9"
down_revision = "5f1f5bc6b44e"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "documents", sa.Column("repository_id", sa.BigInteger(), nullable=True)
    )
    op.create_foreign_key(
        "fk_documents_repository_id",
        "documents",
        "repositories",
        ["repository_id"],
        ["id"],
        ondelete="CASCADE",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("fk_documents_repository_id", "documents", type_="foreignkey")
    op.drop_column("documents", "repository_id")
    # ### end Alembic commands ###
