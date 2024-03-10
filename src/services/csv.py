from models import List, ListExistsError, Session, Task, TaskExistsError
from os import linesep
from datetime import datetime


# cute little function
def export():
    with Session() as session:
        return linesep.join(
            [
                ",".join(("list", "task", "desc", "done", "date")),
                linesep.join(
                    [
                        ",".join([list] + [str(entry) for entry in task])
                        for list in [list.name for list in session.query(List).all()]
                        for task in [
                            [
                                task.id,
                                task.desc,
                                int(task.done),
                                str(task.duefor) if task.duefor else "",
                            ]
                            for task in session.query(Task).filter_by(list=list).all()
                        ]
                    ]
                ),
            ]
        )


def _import(csv: str):
    """Import from CSV headless data."""
    lists = []
    for line in csv.splitlines():
        line = line.split(",")
        list = line[0]
        task = int(line[1])
        desc = line[2]
        done = bool(int(line[3]))
        date = datetime.strptime(line[4], "%Y-%m-%d") if line[4] else None
        if list not in lists:
            try:
                List.create(list)
            except ListExistsError as e:
                print("list already exists: " + str(e))
            lists.append(list)
        try:
            Task.create(desc, list, date, id=task, done=done)
        except TaskExistsError as e:
            print("task already exists, replacing: " + str(e))
            Task.delete(list, task)
            Task.create(desc, list, date, id=task, done=done)
