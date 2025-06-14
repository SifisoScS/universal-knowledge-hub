from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required
from app.models import User
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method != 'POST':
        return render_template('register.html')
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    
    if User.query.filter_by(email=email).first():
        flash('Email already registered.', 'error')
        return redirect(url_for('auth.register'))
    if User.query.filter_by(username=username).first():
        flash('Username already taken.', 'error')
        return redirect(url_for('auth.register'))
        
    new_user = User(
        username=username,
        email=email,
        created_at=datetime.utcnow()
    )
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    
    flash('Registration successful! Please log in.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.index'))
        flash('Invalid email or password.', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))