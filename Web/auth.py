from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

# Отвечает за вход в аккаунт
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if user.password == password:
                flash('Вы успешно вошли в аккаунт', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Неверный пароль', category='error')
        else:
            flash('Аккаунта с такой почтой не существует', category='error')

    return render_template("login.html", user=current_user)

# Отвечает за выход из аккаунта
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# Отвечает за регистрацию
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == "POST":
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Аккаунт с такой почтой уже существует', category='error')
        elif len(email) < 4:
            flash("Почтовый адрес должен быть длиннее 4 символов", category="error")
        elif len(firstName) < 2:
            flash("Имя должно состоять хотя бы из одного символа", category="error")
        elif password1 != password2:
            flash("Пароли не совпадают", category="error")
        elif len(password1) < 7:
            flash("Пароль должен быть длиннее 7 символов", category="error")
        else:
            new_user = User(email=email, firstName=firstName, password=password1)

            db.session.add(new_user)
            db.session.commit()

            flash("Аккаунт создан", category="success")
            return redirect(url_for('auth.login'))
        
    return render_template("sign_up.html", user=current_user)
