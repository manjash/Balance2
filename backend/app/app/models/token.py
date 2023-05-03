from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from . import User  # noqa: F401


class Token(Base):
    token = Column(String, primary_key=True, index=True)
    is_valid = Column(Boolean, default=True)
    authenticates_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    authenticates: Mapped["User"] = relationship(back_populates="refresh_tokens")
