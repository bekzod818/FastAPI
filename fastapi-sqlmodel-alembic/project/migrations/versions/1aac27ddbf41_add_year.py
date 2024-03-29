"""add year

Revision ID: 1aac27ddbf41
Revises: f22aad45aae7
Create Date: 2024-02-13 03:32:00.557215

"""
from typing import Sequence, Union

from alembic import op

import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "1aac27ddbf41"
down_revision: Union[str, None] = "f22aad45aae7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("song", sa.Column("year", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_song_year"), "song", ["year"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_song_year"), table_name="song")
    op.drop_column("song", "year")
    # ### end Alembic commands ###
