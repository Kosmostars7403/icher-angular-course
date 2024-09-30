from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Integer, ForeignKey, String, TIMESTAMP, Boolean, BigInteger, BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.db import Base

if TYPE_CHECKING:
    from application.personal_chat.models import PersonalChat


class Message(Base):
    __tablename__ = 'message'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_from_id: Mapped[BigInteger] = mapped_column(BIGINT, ForeignKey('user.id'))
    personal_chat_id: Mapped[int] = mapped_column(Integer, ForeignKey('personal_chat.id'))
    text: Mapped[str] = mapped_column(String)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP, onupdate=datetime.utcnow)

    personal_chat: Mapped['PersonalChat'] = relationship('PersonalChat')
