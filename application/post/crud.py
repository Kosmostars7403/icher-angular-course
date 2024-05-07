from sqlalchemy.orm import Session
from datetime import datetime
from . import models


def create_post(db: Session, title: str, content: str, author_id: int):
    new_post = models.Post(
        title=title,
        content=content,
        author=author_id,
        created_at=datetime.utcnow()
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


def get_post(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()


def get_all_posts(db: Session):
    return db.query(models.Post).all()

