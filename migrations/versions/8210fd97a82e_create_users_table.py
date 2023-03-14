"""Create users table

Revision ID: 8210fd97a82e
Revises: 
Create Date: 2023-03-14 17:14:20.294741

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8210fd97a82e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('first_name', sa.Unicode(length=255), nullable=False),
    sa.Column('last_name', sa.Unicode(length=255), nullable=True),
    sa.Column('email', sa.Unicode(length=255), nullable=False),
    sa.Column('password', sa.Unicode(length=255), nullable=False),
    sa.Column('last_login', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    # ### end Alembic commands ###
