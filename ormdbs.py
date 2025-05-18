from calendar import c
from flask_login import current_user
from sqlalchemy import BLOB, create_engine, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
import asyncio
from config import settings
from typing import Optional



engine = create_engine("sqlite:///:user.db", echo=True)

session_factory = sessionmaker(engine)



class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class Users(Base):
    __tablename__ = "user"

    user: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()
    balance: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(default="раб")

class Posts(Base):
    __tablename__ = "post"

    post: Mapped[str] = mapped_column()
    imag = mapped_column(BLOB)
    user: Mapped[str] = mapped_column()
    likes: Mapped[int] = mapped_column(default=0)
    liked: Mapped[str] = mapped_column(default="")



def create_db() -> None:
    Base.metadata.create_all(engine)

def insert_orm_user(name: str, password: str) -> None:
    with session_factory() as ses:
        user = Users(user=name, password=password)
        ses.add(user)
        ses.commit()

def insert_orm_post(post: str, user: str, image: Optional[BLOB] = None) -> None:
    with session_factory() as ses:
        post = Posts(post=post, imag=image, user=user,)
        ses.add(post)
        ses.commit()

def select_posts() -> None:
    with engine.connect() as conn:
        check = conn.execute(select(Posts).limit(10)).all()
    return reversed(check)

def get_image(id: int) -> BLOB:
    with engine.connect() as conn:
        check = conn.execute(select(Posts.imag).where(Posts.id == id)).scalar()
    return check
    
def update_likes(id: int) -> None:
    with session_factory() as ses:
        post = ses.get(Posts, id)
        post.likes += 1
        ses.commit()

def update_dislikes(id: int) -> None:
    with session_factory() as ses:
        post = ses.get(Posts, id)
        post.likes -= 1
        ses.commit()

def update_liked(id: int) -> None:
    with session_factory() as ses:
        post = ses.get(Posts, id)
        post.liked += f";{current_user.name}"
        ses.commit()

def update_disliked(id: int) -> None:
    with session_factory() as ses:
        post = ses.get(Posts, id)
        liked = post.liked.split(";")
        liked.remove(current_user.name)
        post.liked = ";".join(liked)
        ses.commit()

def get_liked(id: int) -> None:
    with session_factory() as ses:
        check = ses.get(Posts, id)
    return check.liked

def select_from_orm(name: str, what: classmethod) -> int | str:
    with engine.connect() as conn:
        check = conn.execute(select(what).where(Users.user == name)).scalar()
    return check

def select_orm_equal(id: int, what: classmethod) -> str:
    with engine.connect() as conn:
        check = conn.execute(select(what).where(Users.id == id)).scalar()
    return check


if __name__ == "__main__":
    select_posts()
