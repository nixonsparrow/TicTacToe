import os


class Config:
    STATIC_FOLDER = f"{os.getenv('APP_FOLDER')}/tictactoe/static"
    SECRET_KEY = os.environ.get("SECRET_KEY", "InseCuresecretKey123456!@#$%^oiesrao@#ihageh23gaw4")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
