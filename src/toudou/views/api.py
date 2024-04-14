from datetime import date
from flask import Blueprint
from toudou.models import List, ListNotFoundError, Task, ListExistsError
from spectree import SpecTree
from pydantic.v1 import BaseModel, conlist, constr, condate, conint

spec = SpecTree("flask", annotations=True)

api = Blueprint(
    "api",
    __name__,
    url_prefix="/",
    static_url_path="../static",
    template_folder="../templates",
)


# doing it the Python way
def real(o, check=False):
    if check:
        o.__getreal__(checklist=check)
    return o.__getreal__()


class ConstrainedTask(BaseModel):
    desc: constr(max_length=255)  # type: ignore
    duefor: condate(gt=date(1980, 1, 1), lt=date(3000, 1, 1))  # type: ignore
    list: constr(max_length=255)  # type: ignore
    id: conint(lt=255) = None  # type: ignore
    done: bool = False

    def __getreal__(self, checklist=False) -> Task:
        if checklist and not List.exists(self.list):
            raise ListNotFoundError("can't create Task object: list not found")
        return Task(self.desc, self.duefor, self.list, id=self.id, done=self.done)


class ConstrainedList(BaseModel, List):
    name: constr(max_length=255)  # type: ignore
    items: conlist(ConstrainedTask, max_items=255, unique_items=1)  # type: ignore

    def __getreal__(self) -> List:
        return List(self.name, [real(task) for task in self.items])


class Lists(BaseModel):
    inner: conlist(ConstrainedList, max_items=255, unique_items=1)  # type: ignore

    def __getreal__(self) -> list[List]:
        return [real(list) for list in self.inner]


@api.post("/lists")
@spec.validate(tags=["api"])
def createlists(lists: Lists):
    try:
        for list in real(lists):
            list.create()
    except ListExistsError as e:
        return f"List `{e}` already exists", 400


@api.post("/list")
@spec.validate(tags=["api"])
def createlist(list: ConstrainedList):
    try:
        real(list).create()
    except ListExistsError:
        return "List already exists", 400


@api.get("/lists")
def readlists():
    return {list.name: dict(list) for list in List.all()}


@api.get("/list/<name>")
def readlist(name: str):
    try:
        return dict(List.read(name))
    except ListNotFoundError:
        return "List not found", 400


@api.patch("/lists")
@spec.validate(tags=["api"])
def updatelists(lists: Lists):
    delalllists()
    createlists(lists)


@api.patch("/list/<name>")
@spec.validate(tags=["api"])
def updatelist(name: str, list: ConstrainedList):
    List.read(name).delete()
    createlist(list)


@api.delete("/lists")
def delalllists():
    for list in List.all():
        list.delete()


@api.delete("/list/<name>")
def dellist(name: str):
    try:
        List.read(name).delete()
    except ListNotFoundError:
        return "List not found", 400
