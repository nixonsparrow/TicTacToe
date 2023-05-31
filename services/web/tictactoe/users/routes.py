from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from tictactoe import bcrypt, db
from tictactoe.models import User
from tictactoe.users.forms import LoginForm, RegistrationForm, UpdateAccountForm

users = Blueprint("users", __name__)


@users.route("/register", methods=["GET", "POST"])
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for("main.homepage"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(
            f"Account has been created for you, {user.username}. You can now log in.",
            "success",
        )
        return redirect(url_for("users.login_page"))
    return render_template("register.html", title="Register", form=form)


@users.route("/login", methods=["GET", "POST"])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        try:
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user=user, remember=form.remember.data)
                flash(f"{user.username}, you have been logged in!", "success")
                next_page = request.args.get("next")
                return (
                    redirect(next_page)
                    if next_page
                    else redirect(url_for("main.homepage"))
                )
        except ValueError:
            pass
        flash("Login unsuccessful. Please check username and password", "danger")
    return render_template("login.html", title="Login", form=form)


@users.route("/logout", methods=["GET"])
def logout():
    logout_user()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("main.homepage"))


@users.route("/account", methods=["GET", "POST"])
@login_required
def account_page():
    form = UpdateAccountForm(username=current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()
        flash("Your account has been updated.", "success")
        return redirect(url_for("users.account_page"))
    elif request.method == "GET":
        form.username.data = current_user.username
    return render_template("account.html", title="Account", form=form)
