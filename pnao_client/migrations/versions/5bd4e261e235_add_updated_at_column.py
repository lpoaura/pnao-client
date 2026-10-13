"""Ajouter updated_at à raw_data sans modifier les données existantes.

Revision ID: 5bd4e261e235
Revises: 0b618d095e8c
Create Date: 2026-10-13 14:45:34.924640
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "5bd4e261e235"
down_revision: Union[str, Sequence[str], None] = "0b618d095e8c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ajouter l'horodatage et renseigner les lignes existantes."""
    op.add_column(
        "raw_data",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        schema="pnao",
    )


def downgrade() -> None:
    """Retirer uniquement la colonne ajoutée par cette migration."""
    op.drop_column("raw_data", "updated_at", schema="pnao")
