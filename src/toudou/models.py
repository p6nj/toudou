from contextlib import contextmanager
from dataclasses import dataclass
from os import linesep
from typing import Self
from sqlalchemy import Row, create_engine, text
from datetime import date
from py8fact import random_fact
from toudou.config import config

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
            for line in file.readlines():
                session.execute(text(line))


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


@dataclass
class Task:
    __tablename__ = "task"
    desc: str
    duefor: date
    list: str
    id: int = None
    done: bool = False

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, desc='{self.desc}', done={self.done}, duefor='{self.duefor}', list='{self.list}')>"

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
                text(
                    f"select * from {Task.__tablename__}"
                    + " where list={list}" * bool(list)
                )
            ).fetchall()

    @staticmethod
    def exists(id: int, list: str) -> Self:
        with Session() as session:
            return session.execute(
                text(
                    f"select * from {Task.__tablename__} where id=:id and list=:list"
                ).params(id=id, list=list)
            ).fetchone()

    @staticmethod
    def from_row(row: Row[int, str, bool, date | None, str]) -> Self:
        return Task(
            row.desc,
            row.duefor,
            row.list,
            id=row.id,
            done=row.done,
        )

    def create(self):
        if not self.id or not Task.exists(self.id, self.list):
            with Session(commit=True) as session:
                session.execute(
                    text(
                        f"insert into {Task.__tablename__}(id, desc, done, duefor, list)"
                        "values (:id, :desc, :done, :duefor, :list)"
                    ).params(
                        id=self.id,
                        desc=self.desc,
                        done=self.done,
                        duefor=self.duefor,
                        list=self.list,
                    )
                )
        else:
            raise TaskExistsError(self.id)

    @staticmethod
    def read(id: int, list: str) -> Self:
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
                    text(
                        f"update {Task.__tablename__} set desc=:desc where id=:id and list=:list"
                    ).params(desc=desc, id=self.id, list=self.list)
                )
            if done is not None:
                session.execute(
                    text(
                        f"update {Task.__tablename__} set done=:done where id=:id and list=:list"
                    ).params(done=done, id=self.id, list=self.list)
                )
            if duefor is not None:
                session.execute(
                    text(
                        f"update {Task.__tablename__} set duefor=:duefor where id=:id and list=:list"
                    ).params(duefor=duefor, id=self.id, list=self.list)
                )

    def delete(self):
        with Session(commit=True) as session:
            session.execute(
                text(
                    f"delete from {Task.__tablename__} where id=:id and list=:list"
                ).params(id=self.id, list=self.list)
            )


@dataclass
class List:
    __tablename__ = "list"
    name: str
    items: list[Task]

    def __repr__(self) -> str:
        return f"<List(name='{self.name}')>"

    def __str__(self) -> str:
        return (
            linesep.join([f"{t.id}\t{t}" for t in self.items])
            if self.items
            else "Nothing to do." + linesep + "Did you know? " + random_fact()
        )

    @staticmethod
    def all() -> list[Self]:
        with Session() as session:
            return session.execute(
                text(f"select * from {List.__tablename__}")
            ).fetchall()

    @staticmethod
    def from_row(row: Row[str]) -> Self:
        return List.empty(row.name).with_items()

    @staticmethod
    def exists(name: str) -> Row[str] | None:
        with Session() as session:
            return session.execute(
                text(f"select * from {List.__tablename__} where name=:name").params(
                    name=name
                )
            ).fetchone()

    def create(self):
        if not List.exists(self.name):
            with Session(commit=True) as session:
                session.execute(
                    text(f"insert into {List.__tablename__} values (:name)").params(
                        name=self.name
                    )
                )
        else:
            raise ListExistsError(self.name)

    @staticmethod
    def read(name: str) -> Self:
        if row := List.exists(name):
            return List.from_row(row)
        else:
            raise ListNotFoundError(name)

    def with_items(self) -> Self:
        with Session() as session:
            self.items = [
                Task.from_row(r)
                for r in session.execute(
                    text(f"select * from {Task.__tablename__} where list=:list").params(
                        list=self.name
                    )
                ).fetchall()
            ]
        return self

    @staticmethod
    def empty(name: str) -> Self:
        return List(name, [])

    def update(self, name: str):
        with Session(commit=True) as session:
            session.execute(
                text(
                    f"update {List.__tablename__} set name=:name where name=:selfname"
                ).params(name=name, selfname=self.name)
            )

    def delete(self):
        with Session(commit=True) as session:
            session.execute(
                text(f"delete from {List.__tablename__} where name=:name").params(
                    name=self.name
                )
            )
