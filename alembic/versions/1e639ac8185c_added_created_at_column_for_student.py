"""Added created_at column for Student

Revision ID: 1e639ac8185c
Revises: 9e59866d2eac
Create Date: 2024-09-07 14:07:46.682445

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e639ac8185c'
down_revision: Union[str, None] = '9e59866d2eac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('students', sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('students', 'created_at')
    # ### end Alembic commands ###
