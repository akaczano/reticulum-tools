from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import TIMESTAMP
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[str] = mapped_column(primary_key = True)
    text: Mapped[str]
    source: Mapped[str]
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False))


class Contact(Base):
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(primary_key=True)
    hash: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    last_updated: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False))
    