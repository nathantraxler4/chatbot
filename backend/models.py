from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(), # Tells SQLAlchemy the DB will supply a default
        nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    
class Message(Base, TimestampMixin):
    __tablename__ = "message"

    # columns
    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(String, nullable=False) # Would be better as an enum
    content: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self) -> str:
            return f"Message(id={self.id!r}, content={self.content!r})"
