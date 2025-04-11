from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, insert, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

engine: Engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

session_factory = sessionmaker(engine)

md = MetaData()

user_table = Table(
    "users",
    md,
    Column(
         "id",
         Integer,
         primary_key=True,
         autoincrement=True,
     ),
     Column(
         "user",
        String,
    ),
     Column(
         "password",
         String,
     )
     )
md.drop_all(engine)
md.create_all(engine)


class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = "user"


    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()

Base.metadata.create_all(engine)

def insert_orm_user(user, password):
    with session_factory() as ses:
        user = Users(user="bobr", password="123")
        ses.add(user)
        ses.commit()

def select_orm_all():
    with session_factory() as ses:
        res = ses.get(Users, 1)
        print(res)

def insert_user(user, password):
    with engine.connect() as conn:
        conn.execute(insert(user_table).values(user=user, password=password))
        conn.commit()


def select_all():
    with engine.connect() as conn:
        res = conn.execute(select(user_table))
    return res.all()

if __name__ == "__main__":
    insert_user("vova", "123")
    print(select_all())

    insert_orm_user("Rinde", "123")
    select_orm_all()