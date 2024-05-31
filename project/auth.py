from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, login_required, logout_user
from .models import User
from .db_conn import get_user, add_user

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():

    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    users = get_user(email)  # (id, email, name, password)

    if len(users) == 0 or not (users[0][3] == password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))
    
    user = users[0]

    user_obj = User(user[0])

    login_user(user_obj, remember=remember)

    next_url = request.form.get("next")

    if next_url:
        return redirect(next_url)

    return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    users = get_user(email)
    if len(users) != 0:
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    add_user(email=email, name=name, password=password)

    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

