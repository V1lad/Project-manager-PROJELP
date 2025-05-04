from flask import Blueprint, render_template
from flask_login import login_required, current_user
from . import db

views = Blueprint('views', __name__)

# Показывает главную страницу
@views.route('/')
def main_():
    return render_template("main.html", user=current_user)

# Показывает страницу с информацией об аккаунте
@views.route('/home')
@login_required
def home():
    return render_template("home.html", user=current_user, db=db)