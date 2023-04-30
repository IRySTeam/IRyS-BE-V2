"""remove file-content-str from document table

Revision ID: 4f84fbf3af30
Revises: 0a87bdcb16d7
Create Date: 2023-04-30 16:39:01.426844

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4f84fbf3af30"
down_revision = "0a87bdcb16d7"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("documents", "file_content_str")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "documents",
        sa.Column("file_content_str", sa.TEXT(), autoincrement=False, nullable=True),
    )
    # ### end Alembic commands ###
