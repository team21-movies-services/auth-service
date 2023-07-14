"""init_schema_auth

Revision ID: 929cd3e282d6
Revises: 
Create Date: 2023-06-10 14:49:45.691289

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '929cd3e282d6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE SCHEMA "auth"')


def downgrade() -> None:
    op.execute('DROP SCHEMA "auth"')
