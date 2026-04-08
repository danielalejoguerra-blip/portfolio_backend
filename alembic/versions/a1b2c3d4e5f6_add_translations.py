"""add_translations

Revision ID: a1b2c3d4e5f6
Revises: ff8c92764a89
Create Date: 2025-01-28 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'ff8c92764a89'
branch_labels = None
depends_on = None

TABLES = [
    'projects',
    'blog_posts',
    'courses',
    'education',
    'experiences',
    'skills',
    'personal_info',
]


def upgrade() -> None:
    for table in TABLES:
        op.add_column(
            table,
            sa.Column(
                'translations',
                sa.JSON(),
                server_default='{}',
                nullable=False,
            ),
        )


def downgrade() -> None:
    for table in TABLES:
        op.drop_column(table, 'translations')
