from sqlalchemy import create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

engine = create_engine("sqlite+pysqlite:///user.db", echo=True)

session_factory = sessionmaker(engine)


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()


def create_db():
    Users.metadata.create_all(engine)


def insert_orm_user(name, password):
    with session_factory() as ses:
        user = Users(user=name, password=password)
        ses.add(user)
        ses.commit()


def select_orm(name, what):
    with engine.connect() as conn:
        check = conn.execute(select(what).where(Users.user == name)).scalar()
    return check


def select_orm_equal(id, what):
    with engine.connect() as conn:
        check = conn.execute(select(what).where(Users.id == id)).scalar()
    return check


if __name__ == "__main__":
    insert_orm_user("Rinde", "123")
    select_orm(Users.id, "rinde")
