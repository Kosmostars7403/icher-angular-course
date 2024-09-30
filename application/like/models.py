from typing import TYPE_CHECKING

from sqlalchemy import Integer, ForeignKey, BigInteger, BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.db import Base

if TYPE_CHECKING:
    from application.post.models import Post

class Like(Base):
    __tablename__ = 'like'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[BigInteger] = mapped_column(BIGINT, ForeignKey('user.id'))
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey('post.id'))

    post: Mapped['Post'] = relationship(back_populates='likes')
