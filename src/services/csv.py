from models import List, Session, Task
from os import linesep


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


def _import():
    pass
