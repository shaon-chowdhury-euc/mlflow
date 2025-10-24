"""fix model version varchar properly handling any prior state

Create Date: 2025-10-24 02:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text

# revision identifiers, used by Alembic.
revision = "def789ghi012"
down_revision = "abc123def456"
branch_labels = None
depends_on = None


def upgrade():
    """
    Robustly fix model_versions.version and model_version_tags.version column types.
    
    This migration handles any prior state (INTEGER, VARCHAR, or partial migration).
    """
    bind = op.get_bind()
    inspector = inspect(bind)
    
    # Check current column types
    mv_columns = {col['name']: col for col in inspector.get_columns('model_versions')}
    mvt_columns = {col['name']: col for col in inspector.get_columns('model_version_tags')}
    
    mv_version_type = str(mv_columns['version']['type']).lower()
    mvt_version_type = str(mvt_columns['version']['type']).lower()
    
    # Only proceed if either column is still INTEGER
    if 'int' in mv_version_type or 'int' in mvt_version_type:
        # Step 1: Drop foreign key constraint if it exists
        fk_constraints = inspector.get_foreign_keys('model_version_tags')
        fk_exists = any(fk['name'] == 'model_version_tags_name_version_fkey' 
                       for fk in fk_constraints)
        
        if fk_exists:
            op.drop_constraint(
                "model_version_tags_name_version_fkey",
                "model_version_tags",
                type_="foreignkey"
            )
        
        # Step 2: Alter columns to VARCHAR if needed
        if 'int' in mv_version_type:
            op.alter_column(
                "model_versions",
                "version",
                existing_type=sa.Integer(),
                type_=sa.String(256),
                existing_nullable=False
            )
        
        if 'int' in mvt_version_type:
            op.alter_column(
                "model_version_tags",
                "version",
                existing_type=sa.Integer(),
                type_=sa.String(256),
                existing_nullable=False
            )
        
        # Step 3: Re-create foreign key constraint if it was dropped
        if fk_exists:
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
    Revert to INTEGER type (not recommended).
    """
    bind = op.get_bind()
    inspector = inspect(bind)
    
    # Drop foreign key
    fk_constraints = inspector.get_foreign_keys('model_version_tags')
    fk_exists = any(fk['name'] == 'model_version_tags_name_version_fkey' 
                   for fk in fk_constraints)
    
    if fk_exists:
        op.drop_constraint(
            "model_version_tags_name_version_fkey",
            "model_version_tags",
            type_="foreignkey"
        )
    
    # Revert columns
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
    
    # Re-create foreign key
    op.create_foreign_key(
        "model_version_tags_name_version_fkey",
        "model_version_tags",
        "model_versions",
        ["name", "version"],
        ["name", "version"],
        onupdate="cascade"
    )

