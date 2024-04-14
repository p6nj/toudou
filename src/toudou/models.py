from __future__ import annotations
from contextlib import contextmanager
from dataclasses import dataclass
from os import linesep
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

    def __iter__(self):
        for tuple in {
            "desc": self.desc,
            "date": self.duefor,
            "done": self.done,
        }.items():
            yield tuple

    @staticmethod
    def all(list: str = None) -> list_[Task]:  # type: ignore
        with Session() as session:
            return [
                Task.from_row(row)
                for row in session.execute(
                    text(
                        f"select * from {Task.__tablename__}"
                        + f" where list='{list}'" * bool(list)
                    )
                ).fetchall()
            ]

    @staticmethod
    def exists(id: int, list: str) -> Task:
        with Session() as session:
            return session.execute(
                text(
                    f"select * from {Task.__tablename__} where id=:id and list=:list"
                ).params(id=id, list=list)
            ).fetchone()

    @staticmethod
    def from_row(row: Row[int, str, bool, date | None, str]) -> Task:
        return Task(
            row.desc,
            row.duefor,
            row.list,
            id=row.id,
            done=row.done,
        )

    @staticmethod
    def __nextId(list: str) -> int:
        """Next available ID for a task (because autoincrement doesn't work)"""
        return min(tasks, key=lambda task: task.id) if (tasks := Task.all(list)) else 0

    def create(self):
        if (not self.id) or (not Task.exists(self.id, self.list)):
            with Session(commit=True) as session:
                session.execute(
                    text(
                        f"insert into {Task.__tablename__}(id, desc, done, duefor, list)"
                        "values (:id, :desc, :done, :duefor, :list)"
                    ).params(
                        id=self.id if self.id else Task.__nextId(self.list),
                        desc=self.desc,
                        done=self.done,
                        duefor=self.duefor,
                        list=self.list,
                    )
                )
        else:
            raise TaskExistsError(self.id)

    @staticmethod
    def read(id: int, list: str) -> Task:
        if row := Task.exists(id, list):
            return Task.from_row(row)
        else:
            raise TaskNotFoundError(id)

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

    def __iter__(self):
        for tuple in {item.id: dict(item) for item in self.items}.items():
            yield tuple

    @staticmethod
    def all() -> list[List]:
        with Session() as session:
            return [
                List.from_row(row)
                for row in session.execute(
                    text(f"select * from {List.__tablename__}")
                ).fetchall()
            ]

    @staticmethod
    def from_row(row: Row[str]) -> List:
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
    def read(name: str) -> List:
        if row := List.exists(name):
            return List.from_row(row)
        else:
            raise ListNotFoundError(name)

    def with_items(self) -> List:
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
    def empty(name: str) -> List:
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
