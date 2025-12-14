"""Initial migration: create categories and articles tables

Revision ID: ef546f274885
Revises: 
Create Date: 2025-12-14 15:17:12.143826

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef546f274885'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - create categories and articles tables."""
    # Create categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title_en', sa.String(length=255), nullable=False),
        sa.Column('title_ru', sa.String(length=255), nullable=True),
        sa.Column('title_uz', sa.String(length=255), nullable=True),
        sa.Column('title_es', sa.String(length=255), nullable=True),
        sa.Column('title_he', sa.String(length=255), nullable=True),
        sa.Column('description_en', sa.Text(), nullable=True),
        sa.Column('description_ru', sa.Text(), nullable=True),
        sa.Column('description_uz', sa.Text(), nullable=True),
        sa.Column('description_es', sa.Text(), nullable=True),
        sa.Column('description_he', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)

    # Create articles table
    op.create_table(
        'articles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('title_en', sa.String(length=255), nullable=False),
        sa.Column('title_ru', sa.String(length=255), nullable=True),
        sa.Column('title_uz', sa.String(length=255), nullable=True),
        sa.Column('title_es', sa.String(length=255), nullable=True),
        sa.Column('title_he', sa.String(length=255), nullable=True),
        sa.Column('description_en', sa.Text(), nullable=True),
        sa.Column('description_ru', sa.Text(), nullable=True),
        sa.Column('description_uz', sa.Text(), nullable=True),
        sa.Column('description_es', sa.Text(), nullable=True),
        sa.Column('description_he', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_articles_id'), 'articles', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema - drop articles and categories tables."""
    op.drop_index(op.f('ix_articles_id'), table_name='articles')
    op.drop_table('articles')
    op.drop_index(op.f('ix_categories_id'), table_name='categories')
    op.drop_table('categories')
