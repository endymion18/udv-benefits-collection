"""add poll tables

Revision ID: b72e8b0788d3
Revises: b8305739e669
Create Date: 2024-10-26 13:25:34.698164

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b72e8b0788d3'
down_revision: Union[str, None] = 'b8305739e669'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('poll_status',
    sa.Column('status', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('status')
    )
    op.create_table('poll_results',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('create_date', sa.DateTime(), nullable=True),
    sa.Column('selected_benefits', postgresql.ARRAY(sa.Integer()), nullable=True),
    sa.Column('satisfaction_rate', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.execute("INSERT INTO poll_status VALUES ('False')")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('poll_results')
    op.drop_table('poll_status')
    # ### end Alembic commands ###
