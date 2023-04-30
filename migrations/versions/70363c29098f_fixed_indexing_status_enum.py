"""fixed indexing status enum

Revision ID: 70363c29098f
Revises: 1b884479238c
Create Date: 2023-05-01 03:14:40.793297

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op
from app.document.enums.document import IndexingStatusEnum

# revision identifiers, used by Alembic.
revision = "70363c29098f"
down_revision = "1b884479238c"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("document_indexes", "status")
    op.execute("DROP TYPE indexingstatusenum")
    indexingstatusenum = postgresql.ENUM(IndexingStatusEnum, name="indexingstatusenum")
    indexingstatusenum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        'document_indexes', 
        sa.Column(
            'status',  
            indexingstatusenum,
            nullable=False,
            server_default="READY",
        ),
    ),

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("document_indexes", "status")
    op.execute("DROP TYPE indexingstatusenum")
    indexingstatusenum = postgresql.ENUM(IndexingStatusEnum, name="indexingstatusenum")
    indexingstatusenum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        'document_indexes', 
        sa.Column(
            'status',  
            indexingstatusenum,
            nullable=False,
            server_default="READY",
        ),
    ),
    # ### end Alembic commands ###
