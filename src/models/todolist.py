from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from os import linesep
from typing import Self
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    create_engine,
    select,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

engine = create_engine("sqlite:///td.db", echo=True)
Base = declarative_base()
ToudouDBSession = sessionmaker(bind=engine)


@contextmanager
def Session(*, commit=False):
    session = ToudouDBSession()
    try:
        yield session
        if commit:
            session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def strike(text):
    result = ""
    for c in text:
        result = result + "\u0336" + c
    return result


class ListExistsError(Exception):
    pass


class ListNotFoundError(Exception):
    pass


class TaskNotFoundError(Exception):
    pass


class List(Base):
    __tablename__ = "list"
    name = Column(String, primary_key=True)

    def __repr__(self):
        return f"<List(name='{self.name}')>"

    @staticmethod
    def exists(name: str, session: sessionmaker[Session]):
        return session.query(List).filter_by(name=name).first()

    @staticmethod
    def create(name: str):
        with Session(commit=True) as session:
            if not (list := List.exists(name, session)):
                new_list = List(name=name)
                session.add(new_list)
            else:
                raise ListExistsError(list)

    @staticmethod
    def read(name: str) -> Self:
        with Session() as session:
            if list := List.exists(name, session):
                return list
            else:
                raise ListNotFoundError()

    @staticmethod
    def update(name: str, newname: str):
        with Session(commit=True) as session:
            if list := List.exists(name, session):
                list.name = newname
            else:
                raise ListNotFoundError()

    @staticmethod
    def delete(name: str):
        with Session(commit=True) as session:
            if list := List.exists(name, session):
                session.delete(list)


class Task(Base):
    __tablename__ = "task"
    id = Column(Integer, primary_key=True)
    desc = Column(String, nullable=False)
    done = Column(Boolean, default=False)
    duefor = Column(Date)
    list = Column(String, ForeignKey("list.name"))
    list = relationship("List", back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, desc='{self.desc}', done={self.done}, duefor='{self.duefor}', list='{self.list}')>"

    @staticmethod
    def exists(id: int, list: str, session: sessionmaker[Session]):
        return session.query(List).filter_by(list=list, id=id).first()

    @staticmethod
    def create(desc: str, list: str, duefor: datetime = None):
        with Session(commit=True) as session:
            task = Task(desc=desc, list=list, duefor=duefor)
            session.add(task)

    @staticmethod
    def read(list, id) -> Self:
        with Session() as session:
            if task := Task.exists(id, list, session):
                return task
            else:
                raise TaskNotFoundError()

    @staticmethod
    def update(
        list: str,
        id: int,
        newdesc: str = None,
        newdone: bool = None,
        newduefor: datetime = None,
    ):
        with Session(commit=True) as session:
            if task := Task.exists(id, list, session):
                if newdesc:
                    task.desc = newdesc
                if newdone is not None:
                    task.done = newdone
                if newduefor:
                    task.duefor = newduefor
            else:
                raise TaskNotFoundError()

    @staticmethod
    def delete(list: str, id: int):
        with Session(commit=True) as session:
            if task := Task.exists(id, list, session):
                session.delete(task)


List.tasks = relationship("Task", back_populates="list")
