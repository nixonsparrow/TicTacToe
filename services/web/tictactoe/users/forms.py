from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError

from tictactoe.models import User


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=1, max=40)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign up")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "That username is taken. Please choose different one."
            )


class LoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=1, max=40)]
    )
    # password = PasswordField("Password", validators=[DataRequired()])
    password = PasswordField("Password")
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class UpdateAccountForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=1, max=40)]
    )

    submit = SubmitField("Update")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    "That username is taken. Please choose different one."
                )
