"""Add current task id column

Revision ID: a7375ff9e955
Revises: 02393767a3e9
Create Date: 2023-04-22 20:45:06.826256

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a7375ff9e955"
down_revision = "02393767a3e9"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "document_indexes",
        sa.Column("current_task_id", sa.Unicode(length=255), nullable=True),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("document_indexes", "current_task_id")
    # ### end Alembic commands ###
