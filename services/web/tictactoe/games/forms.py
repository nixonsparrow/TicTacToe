from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError

LEVEL_MIN = 1
LEVEL_MAX = 5


class NewGameSessionForm(FlaskForm):
    level = IntegerField(
        "Level", validators=[DataRequired(), NumberRange(min=LEVEL_MIN, max=LEVEL_MAX)]
    )
    preferred_sign = StringField("Sign", validators=[Length(min=0, max=1)])
    submit = SubmitField("Create")

    def validate_preferred_sign(self, preferred_sign):
        if preferred_sign.data.upper() not in ["", "X", "O"]:
            raise ValidationError(
                "That is not a valid sign. Please choose 'X', 'O' or leave the field empty (random)."
            )

    def validate_level(self, level):
        if level.data > LEVEL_MAX or level.data < LEVEL_MIN:
            raise ValidationError(
                f"That is not a valid level. Please choose value between {LEVEL_MIN} and {LEVEL_MAX} inclusive."
            )


class StatsForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()])
    submit = SubmitField("Apply date filter")
