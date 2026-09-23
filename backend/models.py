"""
models.py – SQLAlchemy ORM model for saved deviations.
"""
import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


def _new_id() -> str:
    return f"DEV-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"


class Deviation(Base):
    __tablename__ = "deviations"

    # Primary key – human-readable deviation ID
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_new_id)

    # ── Section 1: Deviation Information ────────────────────
    site_plant: Mapped[str | None] = mapped_column(String(128))
    date_of_occurrence: Mapped[str | None] = mapped_column(String(32))  # stored as ISO string
    title: Mapped[str | None] = mapped_column(String(256))
    source: Mapped[str | None] = mapped_column(String(64))
    related_product: Mapped[str | None] = mapped_column(String(256))
    batch_lot_number: Mapped[str | None] = mapped_column(String(128))

    # ── Section 2: Deviation Details ────────────────────────
    detailed_description: Mapped[str | None] = mapped_column(Text)
    initial_impact: Mapped[str | None] = mapped_column(String(64))
    initial_severity: Mapped[str | None] = mapped_column(String(64))

    # ── AI Risk Assessment ───────────────────────────────────
    ai_severity_classification: Mapped[str | None] = mapped_column(String(64))
    ai_impact_assessment: Mapped[str | None] = mapped_column(Text)
    ai_suggested_next_action: Mapped[str | None] = mapped_column(Text)
    ai_risk_reasoning: Mapped[str | None] = mapped_column(Text)
    ai_regulatory_risk: Mapped[str | None] = mapped_column(String(16))

    # ── Metadata ─────────────────────────────────────────────
    status: Mapped[str] = mapped_column(String(32), default="Draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
