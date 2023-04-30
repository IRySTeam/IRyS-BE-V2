"""modify document table column

Revision ID: d94665ef3b83
Revises: b89cf41b64d7
Create Date: 2023-04-26 17:11:12.999371

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d94665ef3b83"
down_revision = "dc553cd48a7d"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "documents",
        sa.Column("general_elastic_doc_id", sa.Unicode(length=255), nullable=True),
    )
    op.add_column(
        "documents", sa.Column("mimetype", sa.Unicode(length=255), nullable=True)
    )
    op.add_column(
        "documents", sa.Column("extension", sa.Unicode(length=255), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("documents", "extension")
    op.drop_column("documents", "mimetype")
    op.drop_column("documents", "general_elastic_doc_id")
    # ### end Alembic commands ###