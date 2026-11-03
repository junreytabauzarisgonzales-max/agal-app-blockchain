"""add admin audit logs

Revision ID: a1c9e5d07b42
Revises: 71fed6c08c21
Create Date: 2026-09-19 06:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1c9e5d07b42'
down_revision: Union[str, None] = '71fed6c08c21'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('admin_audit_logs',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('admin_email', sa.String(length=320), nullable=False),
    sa.Column('action', sa.String(length=32), nullable=False),
    sa.Column('resource', sa.String(length=32), nullable=True),
    sa.Column('record_id', sa.String(length=64), nullable=True),
    sa.Column('summary', sa.String(length=500), nullable=True),
    sa.Column('ip_address', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_audit_logs_created_at'), 'admin_audit_logs', ['created_at'], unique=False)
    op.create_index(op.f('ix_admin_audit_logs_action'), 'admin_audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_admin_audit_logs_resource'), 'admin_audit_logs', ['resource'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_admin_audit_logs_resource'), table_name='admin_audit_logs')
    op.drop_index(op.f('ix_admin_audit_logs_action'), table_name='admin_audit_logs')
    op.drop_index(op.f('ix_admin_audit_logs_created_at'), table_name='admin_audit_logs')
    op.drop_table('admin_audit_logs')
