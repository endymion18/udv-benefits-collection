"""add new fields to benefit

Revision ID: 5becbe9465da
Revises: 07d9a8d943d4
Create Date: 2024-11-26 00:29:53.944686

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '5becbe9465da'
down_revision: Union[str, None] = '07d9a8d943d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('benefit', sa.Column('need_confirmation', sa.Boolean(), nullable=False, server_default='False'))
    op.add_column('benefit', sa.Column('need_files', sa.Boolean(), nullable=False, server_default='False'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('benefit', 'need_files')
    op.drop_column('benefit', 'need_confirmation')
    # ### end Alembic commands ###
