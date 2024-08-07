"""Remove ContactInquiry model

Revision ID: e10ea9bab4b2
Revises: 83ff9950a564
Create Date: 2024-08-06 20:58:10.190901

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e10ea9bab4b2'
down_revision = '83ff9950a564'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('contact_inquiry')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('contact_inquiry',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('name', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('email', mysql.VARCHAR(length=120), nullable=False),
    sa.Column('phone', mysql.VARCHAR(length=20), nullable=True),
    sa.Column('organization', mysql.VARCHAR(length=100), nullable=True),
    sa.Column('role', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('message', mysql.TEXT(), nullable=False),
    sa.Column('preferred_contact', mysql.VARCHAR(length=10), nullable=True),
    sa.Column('best_time', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('timestamp', mysql.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_general_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
