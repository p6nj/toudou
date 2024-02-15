from dataclasses import dataclass
from datetime import date
from os import linesep
from sqlite3 import Cursor
from typing import Self


def strike(text):
    result = ""
    for c in text:
        result = result + "\u0336" + c
    return result


class TodoList:
    def __init__(self, name: str, cursor: Cursor) -> None:
        self.items = []
        self.name = name
        self.c = cursor

    def __commit__(self) -> None:
        self.c.connection.commit()

    def exists(self) -> bool:
        return self.c.execute(
            "select 1 from list where name=?", (self.name,)
        ).fetchone()

    def create(self) -> None:
        self.c.execute("insert into list values (?)", (self.name,))
        self.__commit__()

    def __check_remote__(self) -> list[tuple]:
        return [
            TodoList.Item(item[0], item[1], item[3], item[2])
            for item in self.c.execute(
                "select * from task where list=?", (self.name,)
            ).fetchall()
        ]

    def push(self) -> None:
        remote_items = self.__check_remote__()
        for item in self.items:
            if item not in remote_items:
                self.c.execute(
                    "insert into task (id, desc, done, duefor, list) values (?, ?, ?, ?, ?)",
                    (item.id, item.task, item.done, item.date, self.name),
                )
        self.__commit__()

    def pull(self) -> Self:
        self.items = self.__check_remote__()
        return self

    def nuke(self) -> None:
        self.c.execute("delete from list where name=?", (self.name,))
        self.__commit__()

    def nuke_item(self, index: int) -> None:
        self.c.execute("delete from task where list=? and id=?", (self.name, index))
        self.__commit__()

    def __str__(self) -> str:
        return (
            linesep.join([f"{i}\t{t}" for i, t in enumerate(self.items)])
            if self.items
            else "The problem with doing nothing is not knowing when you're finished."
            + linesep
            + "\t\t-- Benjamin Franklin"
        )

    @dataclass
    class Item:
        id: int
        task: str
        date: date | None
        done: bool

        def __str__(self) -> str:
            return (strike(self.task) if self.done else self.task) + (
                " (" + self.date.strftime("%d/%m") + ")"
                if self.date is not None
                else ""
            )
