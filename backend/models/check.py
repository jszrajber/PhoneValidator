from backend.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Boolean, String, DateTime, func
from uuid import UUID as PyUUID
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime


class NumberCheck(Base):
    __tablename__ = "number_check"

    id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    is_valid: Mapped[bool] = mapped_column(Boolean)
    number: Mapped[str] = mapped_column(String(30))
    country: Mapped[str] = mapped_column(String(30))
    country_code: Mapped[str] = mapped_column(String(5))
    carrier: Mapped[str] = mapped_column(String(20), nullable=True)
    type: Mapped[str] = mapped_column(String(10), nullable=True)
    local_format: Mapped[str] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())