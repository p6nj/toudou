from contextlib import contextmanager
from dataclasses import dataclass
from os import linesep
from typing import Self
from sqlalchemy import create_engine, text
from datetime import date
from py8fact import random_fact
from toudou import config

list_ = list

engine = create_engine(config["DATABASE_URL"], echo=config["DEBUG"])


@contextmanager
def Session(*, commit=False):
    session = engine.connect()
    try:
        yield session
        if commit:
            session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def init():
    with Session(commit=1) as session:
        with open("td.sql", "r") as file:
            session.execute(text(file.read()))


def strike(text):
    result = ""
    for c in text:
        result = result + c + "\u0336"
    return result


class ListExistsError(Exception):
    pass


class ListNotFoundError(Exception):
    pass


class TaskExistsError(Exception):
    pass


class TaskNotFoundError(Exception):
    pass


# fake class for type checking purposes
class Task:
    pass


@dataclass
class List:
    __tablename__ = "list"
    name: str
    items: list[Task] = []

    def __repr__(self) -> str:
        return f"<List(name='{self.name}')>"

    def __str__(self) -> str:
        items = List.all()
        return (
            linesep.join([f"{t.id}\t{t}" for t in items])
            if items
            else "Nothing to do." + linesep + "Did you know? " + random_fact()
        )

    @staticmethod
    def all() -> list[Self]:
        with Session() as session:
            return session.execute(f"select * from {List.__tablename__}").fetchall()

    @staticmethod
    def exists(name: str) -> Self | None:
        with Session() as session:
            return session.execute(
                f"select * from {List.__tablename__} where name={name}"
            ).fetchone()

    def create(self):
        if not List.exists(self.name):
            with Session(commit=True) as session:
                session.execute(
                    f"insert into {List.__tablename__} values ({self.name})"
                )
        else:
            raise ListExistsError(self.name)

    @staticmethod
    def read(name: str) -> Self:
        if list := List.exists(name):
            return list
        else:
            raise ListNotFoundError(name)

    def update(self, name: str):
        with Session(commit=True) as session:
            session.execute(
                f"update {List.__tablename__} set name={name} where name={self.name}"
            )

    def delete(self):
        with Session(commit=True) as session:
            session.execute(f"delete from {List.__tablename__} where name={self.name}")


@dataclass
class Task:
    __tablename__ = "task"
    id: int
    desc: str
    done: bool = False
    duefor: date
    list: List

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, desc='{self.desc}', done={self.done}, duefor='{self.duefor}', list='{self.list.name}')>"

    def __str__(self) -> str:
        return (strike(self.desc) if self.done else self.desc) + (
            " (" + self.duefor.strftime("%d/%m") + ")"
            if self.duefor is not None
            else ""
        )

    @staticmethod
    def all(list: str = None) -> list_[Self]:
        with Session() as session:
            return session.execute(
                f"select * from {Task.__tablename__}"
                + " where list={list}" * bool(list)
            ).fetchall()

    @staticmethod
    def exists(id: int, list: str) -> Self:
        with Session() as session:
            return session.execute(
                f"select * from {Task.__tablename__} where id={id} and list={list}"
            ).fetchone()

    def create(self):
        if self.id and not Task.exists(self.id, self.list.name):
            with Session(commit=True) as session:
                session.execute(
                    f"insert into {Task.__tablename__}(id, desc, done, duefor, list)"
                    f"values ({self.id}, {self.desc}, {self.done}, {self.duefor}, {self.list.name})"
                )
        else:
            raise TaskExistsError(self.id)

    @staticmethod
    def read(id: int, list: List) -> Self:
        if list := Task.exists(id, list.name):
            return list
        else:
            raise ListNotFoundError(id)

    def update(
        self,
        desc: str = None,
        done: bool = None,
        duefor: date = None,
    ):
        with Session(commit=True) as session:
            if desc:
                session.execute(
                    f"update {Task.__tablename__} set desc={desc} where id={self.id} and list={self.list.name}"
                )
            if done is not None:
                session.execute(
                    f"update {Task.__tablename__} set done={done} where id={self.id} and list={self.list.name}"
                )
            if duefor is not None:
                session.execute(
                    f"update {Task.__tablename__} set duefor={duefor} where id={self.id} and list={self.list.name}"
                )

    def delete(self):
        with Session(commit=True) as session:
            session.execute(
                f"delete from {Task.__tablename__} where id={self.id} and list={self.list.name}"
            )
