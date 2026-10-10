from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from models import User
from extensions import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('ui.index'))
        flash('Invalid password or email', 'error')
    return render_template('login.html')


@auth_bp.route('/auth/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        password = request.form.get('password')
        if User.query.filter_by(email=email).first():
            flash('Email is already registered.', 'error')
            return render_template('register.html')
        user = User(email=email, first_name=first_name, role='customer')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('ui.index'))
    return render_template('register.html')

@auth_bp.route('/auth/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('ui.index'))
