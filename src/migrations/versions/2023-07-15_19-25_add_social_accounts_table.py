"""add social accounts table

Revision ID: 1260f1d435df
Revises: a4f28511876b
Create Date: 2023-07-15 19:25:29.575041

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '1260f1d435df'
down_revision = 'a4f28511876b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'social_account',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('user_social_id', sa.Text(), nullable=False),
        sa.Column('social_name', sa.Text(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['auth.user.id'], name='auth_social_user_id_fkey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='auth_social_account_pkey'),
        schema='auth',
    )
    op.create_index(
        'social_user_id_user_social_id_uniq',
        'social_account',
        ['user_id', 'user_social_id'],
        unique=True,
        schema='auth',
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('social_user_id_user_social_id_uniq', table_name='social_account', schema='auth')
    op.drop_table('social_account', schema='auth')
    # ### end Alembic commands ###
