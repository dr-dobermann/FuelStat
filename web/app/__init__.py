from flask import Flask
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

flsk = Flask(__name__)
flsk.config["SECRET_KEY"] = "pedaling"

login = LoginManager(flsk)
# Страница, которую получит пользователь, если не авторизуется,
# но захочет зайти на страницу для зарегистированных пользователей
login.login_view = 'login'
login.login_message = "Please Sign In"

bootstrap = Bootstrap(flsk)

from app import routes