from typing import TYPE_CHECKING

from sqlalchemy import Integer, ForeignKey, BigInteger, BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from application.message.models import Message
from database.db import Base

if TYPE_CHECKING:
    from application.message.models import Message
    from application.account.models import User


class PersonalChat(Base):
    __tablename__ = 'personal_chat'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_first_id: Mapped[BigInteger] = mapped_column(BIGINT, ForeignKey('user.id'))
    user_second_id: Mapped[BigInteger] = mapped_column(BIGINT, ForeignKey('user.id'))

    user_first: Mapped['User'] = relationship(foreign_keys=[user_first_id])
    user_second: Mapped['User'] = relationship(foreign_keys=[user_second_id])
    messages: Mapped[list[Message]] = relationship(back_populates='personal_chat', order_by='Message.created_at')
