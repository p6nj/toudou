from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from os import linesep
from typing import Self
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

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


class List(Base):
    __tablename__ = "list"
    name = Column(String, primary_key=True)

    def __repr__(self):
        return f"<List(name='{self.name}')>"

    @staticmethod
    def create(name):
        with Session(commit=True) as session:
            new_list = List(name=name)
            session.add(new_list)
            return new_list


class Task(Base):
    __tablename__ = "task"
    id = Column(Integer, primary_key=True)
    desc = Column(String, nullable=False)
    done = Column(Boolean, default=False)
    duefor = Column(Date)
    list_name = Column(String, ForeignKey("list.name"))
    list = relationship("List", back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, desc='{self.desc}', done={self.done}, duefor='{self.duefor}', list_name='{self.list_name}')>"


List.tasks = relationship("Task", back_populates="list")
