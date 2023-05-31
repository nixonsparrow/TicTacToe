from flask import Blueprint, render_template

main = Blueprint("main", __name__)


@main.route("/")
def homepage():
    context = {"title": "Homepage"}
    return render_template("home.html", **context)


@main.route("/about")
def about_page():
    context = {"title": "About page"}
    return render_template("about.html", **context)
