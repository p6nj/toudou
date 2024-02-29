from dataclasses import dataclass
from datetime import date
from os import linesep
from typing import Self


def strike(text):
    result = ""
    for c in text:
        result = result + "\u0336" + c
    return result


@dataclass
class TodoList:
    items: list[Self.Item]
    name: str

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
