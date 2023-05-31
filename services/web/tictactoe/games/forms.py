from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError

from tictactoe.models import GameSession


class NewGameSessionForm(FlaskForm):
    level = IntegerField("Level")
    preferred_sign = StringField("Sign", validators=[Length(min=0, max=1)])
    submit = SubmitField("Create")

    def validate_preferred_sign(self, preferred_sign):
        if preferred_sign.data.upper() not in ["", "X", "O"]:
            raise ValidationError(
                "That is not a valid sign. Please choose 'X' or 'O'."
            )
