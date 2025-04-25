"""Fix schema mismatch

Revision ID: f10ab080e863
Revises: 026d4ced3bfe
Create Date: 2025-04-24 20:43:52.700902
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = 'f10ab080e863'
down_revision = '026d4ced3bfe'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.alter_column('user_id', existing_type=sa.Integer(), nullable=True)
        batch_op.alter_column('buyer_id', existing_type=sa.Integer(), nullable=True)

        batch_op.create_foreign_key(
            constraint_name='fk_post_user_id',
            referent_table='user',
            local_cols=['user_id'],
            remote_cols=['id']
        )
        batch_op.create_foreign_key(
            constraint_name='fk_post_buyer_id',
            referent_table='user',
            local_cols=['buyer_id'],
            remote_cols=['id']
        )

    with op.batch_alter_table('user', schema=None) as batch_op:
        # 1단계: balance 컬럼 추가 (nullable=True, default=0)
        batch_op.add_column(sa.Column('balance', sa.Integer(), nullable=True, server_default='0'))

    # 2단계: balance 컬럼을 NOT NULL로 변경
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('balance', existing_type=sa.Integer(), nullable=False)



def downgrade():
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_constraint('fk_post_user_id', type_='foreignkey')
        batch_op.drop_constraint('fk_post_buyer_id', type_='foreignkey')

        # rollback 시 NULL 허용 복구
        batch_op.alter_column('user_id', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('buyer_id', existing_type=sa.Integer(), nullable=True)

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('balance', existing_type=sa.Integer(), nullable=True)

