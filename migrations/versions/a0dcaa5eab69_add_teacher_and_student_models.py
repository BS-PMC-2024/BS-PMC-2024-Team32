"""Add teacher and student models

Revision ID: a0dcaa5eab69
Revises: 2680460ac61e
Create Date: 2024-07-28 18:43:46.037046

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a0dcaa5eab69'
down_revision = '2680460ac61e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('teacher',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('manager_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['manager_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('student',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('teacher_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['teacher_id'], ['teacher.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('student')
    op.drop_table('teacher')
    # ### end Alembic commands ###
