"""empty message

Revision ID: f6dac5277df9
Revises: 
Create Date: 2019-12-02 22:25:36.082723

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6dac5277df9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('safe_files',
    sa.Column('file_id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=128), nullable=False),
    sa.Column('size', sa.Integer(), nullable=False),
    sa.Column('sha1', sa.String(length=40), nullable=True),
    sa.Column('md5', sa.String(length=32), nullable=True),
    sa.Column('filetypes', sa.String(length=10), nullable=True),
    sa.PrimaryKeyConstraint('file_id'),
    sa.UniqueConstraint('filename'),
    sa.UniqueConstraint('md5'),
    sa.UniqueConstraint('sha1')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('safe_files')
    # ### end Alembic commands ###
