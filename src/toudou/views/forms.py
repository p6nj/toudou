from flask_wtf import FlaskForm
from wtforms import StringField, DateField, BooleanField
from wtforms.validators import DataRequired, Optional


class Task(FlaskForm):
    """Add a task to the list"""

    desc = StringField("desc", validators=[DataRequired()])
    duefor = DateField("duefor", validators=[Optional()])


class List(FlaskForm):
    """Create a new list"""

    name = StringField("name", validators=[DataRequired()])


class TaskMod(FlaskForm):
    """Modify a task"""

    desc = StringField("desc", validators=[DataRequired()])
    yesdate = BooleanField("yesdate")
    duefor = DateField("duefor", validators=[Optional()])


class ListMod(FlaskForm):
    """Modify a list"""

    name = StringField("name", validators=[DataRequired()])
