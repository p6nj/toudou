from flask_wtf import FlaskForm
from wtforms import StringField, DateField
from wtforms.validators import DataRequired, Optional


class NewTask(FlaskForm):
    desc = StringField("desc", validators=[DataRequired()])
    duefor = DateField("duefor", validators=[Optional()])
