from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database.db import Base


class PersonalChat(Base):
    __tablename__ = 'personal_chat'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_first: Mapped[int] = mapped_column(ForeignKey('user.id'))
    user_second: Mapped[int] = mapped_column(ForeignKey('user.id'))


