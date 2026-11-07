from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import TIMESTAMP
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[str] = mapped_column(primary_key = True)
    source: Mapped[str]
    destination: Mapped[str]
    status: Mapped[int]
    time_sent: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False))
    time_received: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False), nullable=True)
    rssi: Mapped[float] = mapped_column(nullable=True)
    snr: Mapped[float] = mapped_column(nullable=True)
    rtt: Mapped[float] = mapped_column(nullable=True)
    text: Mapped[str]


class Contact(Base):
    __tablename__ = "contacts"    
    hash: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    last_updated: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False))
    