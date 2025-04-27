from sqlalchemy import BLOB, create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

engine = create_engine("sqlite+pysqlite:///user.db", echo=True)

session_factory = sessionmaker(engine)

engine_post = create_engine("sqlite+pysqlite:///post.db", echo=True)

session_factory_post = sessionmaker(engine_post)


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "user"


    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()

class Posts(Base):
    __tablename__ = "post"


    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    post: Mapped[str] = mapped_column()
    imag = mapped_column(BLOB)
    user: Mapped[str] = mapped_column()

def create_db():
    Base.metadata.create_all(engine)

def insert_orm_user(name, password):
    with session_factory() as ses:
        user = Users(user=name, password=password)
        ses.add(user)
        ses.commit()

def insert_orm_post(post, user, image=None):
    with session_factory_post() as ses:
        post = Posts(post=post, imag=image, user=user)
        ses.add(post)
        ses.commit()


def select_orm(name, what):
    with engine.connect() as conn:
        check = conn.execute(select(what).where(Users.user == name)).scalar()
    return check

def select_orm_equal(id, what):
    with engine.connect() as conn:
        check = conn.execute(select(what).where(Users.id == id)).scalar()
    return check

def select_orm(name, what):
    with engine_post.connect() as conn:
        check = conn.execute(select(what).where(Users.user == name)).scalar()
    return check

def select_orm_equal(id, what):
    with engine_post.connect() as conn:
        check = conn.execute(select(what).where(Users.id == id)).scalar()
    return check


if __name__ == "__main__":
    insert_orm_user("Rinde", "123")
    select_orm(Users.id, "rinde")