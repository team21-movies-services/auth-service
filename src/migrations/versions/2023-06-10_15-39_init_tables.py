"""init_tables

Revision ID: a4f28511876b
Revises: 929cd3e282d6
Create Date: 2023-06-10 15:39:28.985900

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a4f28511876b'
down_revision = '929cd3e282d6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('device',
    sa.Column('user_agent', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.PrimaryKeyConstraint('id', name='auth_device_pkey'),
    sa.UniqueConstraint('user_agent', name='auth_device_user_agent_unique'),
    schema='auth'
    )
    op.create_table('role',
    sa.Column('name', sa.String(length=127), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.PrimaryKeyConstraint('id', name='auth_role_pkey'),
    sa.UniqueConstraint('name', name='auth_role_name_unique'),
    schema='auth'
    )
    op.create_table('user',
    sa.Column('first_name', sa.String(length=127), nullable=True),
    sa.Column('last_name', sa.String(length=127), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password', sa.String(length=127), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
    sa.PrimaryKeyConstraint('id', name='auth_user_pkey'),
    sa.UniqueConstraint('email', name='auth_user_email_unique'),
    schema='auth'
    )
    op.create_table('history',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('action_type', postgresql.ENUM('LOGIN', 'LOGOUT', 'CHANGE_PASSWORD', 'CHANGE_INFO', name='action_type'), nullable=False),
    sa.Column('device_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
    sa.ForeignKeyConstraint(['device_id'], ['auth.device.id'], name='device_id__fk'),
    sa.ForeignKeyConstraint(['user_id'], ['auth.user.id'], name='user_id__fk'),
    sa.PrimaryKeyConstraint('id', name='auth_history_pkey'),
    schema='auth'
    )
    op.create_table('user_remember_device',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('device_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
    sa.ForeignKeyConstraint(['device_id'], ['auth.device.id'], name='device_id__fk'),
    sa.ForeignKeyConstraint(['user_id'], ['auth.user.id'], name='user_id__fk'),
    sa.PrimaryKeyConstraint('id', name='auth_user_remember_device_pkey'),
    schema='auth'
    )
    op.create_index('user_remember_device_user_id_device_id_uniq', 'user_remember_device', ['user_id', 'device_id'], unique=True, schema='auth')
    op.create_table('user_role',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('role_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['auth.role.id'], name='role_id__fk'),
    sa.ForeignKeyConstraint(['user_id'], ['auth.user.id'], name='user_id__fk'),
    sa.PrimaryKeyConstraint('id', name='auth_user_role_pkey'),
    schema='auth'
    )
    op.create_index('user_role_user_id_role_id_uniq', 'user_role', ['user_id', 'role_id'], unique=True, schema='auth')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('user_role_user_id_role_id_uniq', table_name='user_role', schema='auth')
    op.drop_table('user_role', schema='auth')
    op.drop_index('user_remember_device_user_id_device_id_uniq', table_name='user_remember_device', schema='auth')
    op.drop_table('user_remember_device', schema='auth')
    op.drop_table('history', schema='auth')
    op.drop_table('user', schema='auth')
    op.drop_table('role', schema='auth')
    op.drop_table('device', schema='auth')
    op.execute('DROP TYPE public.action_type;')
    # ### end Alembic commands ###
