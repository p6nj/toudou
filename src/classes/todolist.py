from dataclasses import dataclass
from datetime import date
from os import linesep


class TodoList:
    def __init__(self) -> None:
        self.items: [TodoList.Item] = []

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
        task: str
        date: date | None
        done: bool

        def __str__(self) -> str:
            return self.task + (" (" + self.date + ")" if self.date is not None else "")
