from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

if TYPE_CHECKING:
    from . import Balance  # noqa: F401
    from . import Token, TransactionEvent


class User(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    modified = Column(DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now(), nullable=False)
    full_name = Column(String, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    totp_secret = Column(String, nullable=True)
    totp_counter = Column(String, nullable=True)
    email_validated = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    refresh_tokens: Mapped[list["Token"]] = relationship(back_populates="authenticates", lazy="dynamic")
    balance = relationship("Balance", back_populates="user")
    transaction_event: Mapped[list["TransactionEvent"]] = relationship(back_populates="user")
