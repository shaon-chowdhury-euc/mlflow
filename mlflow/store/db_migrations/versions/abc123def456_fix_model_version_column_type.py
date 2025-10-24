"""fix model_version column type from integer to varchar

Create Date: 2025-10-24 01:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "abc123def456"
down_revision = "bf29a5ff90ea"
branch_labels = None
depends_on = None


def upgrade():
    """
    Fix model_versions.version and model_version_tags.version column types.
    
    MLflow queries these columns as VARCHAR but they were created as INTEGER,
    causing "operator does not exist: integer = character varying" errors.
    """
    # Drop foreign key constraint
    op.drop_constraint(
        "model_version_tags_name_version_fkey",
        "model_version_tags",
        type_="foreignkey"
    )
    
    # Alter column types to VARCHAR
    op.alter_column(
        "model_versions",
        "version",
        existing_type=sa.Integer(),
        type_=sa.String(256),
        existing_nullable=False
    )
    
    op.alter_column(
        "model_version_tags",
        "version",
        existing_type=sa.Integer(),
        type_=sa.String(256),
        existing_nullable=False
    )
    
    # Re-create foreign key constraint
    op.create_foreign_key(
        "model_version_tags_name_version_fkey",
        "model_version_tags",
        "model_versions",
        ["name", "version"],
        ["name", "version"],
        onupdate="cascade"
    )


def downgrade():
    """
    Revert to INTEGER type (not recommended, will break queries).
    """
    # Drop foreign key constraint
    op.drop_constraint(
        "model_version_tags_name_version_fkey",
        "model_version_tags",
        type_="foreignkey"
    )
    
    # Revert column types to INTEGER
    op.alter_column(
        "model_versions",
        "version",
        existing_type=sa.String(256),
        type_=sa.Integer(),
        existing_nullable=False
    )
    
    op.alter_column(
        "model_version_tags",
        "version",
        existing_type=sa.String(256),
        type_=sa.Integer(),
        existing_nullable=False
    )
    
    # Re-create foreign key constraint
    op.create_foreign_key(
        "model_version_tags_name_version_fkey",
        "model_version_tags",
        "model_versions",
        ["name", "version"],
        ["name", "version"],
        onupdate="cascade"
    )

