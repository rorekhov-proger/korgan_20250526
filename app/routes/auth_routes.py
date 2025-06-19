from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.services.auth_service import AuthService
from app.services.redis_service import RedisService
from app.forms.auth_forms import LoginForm, RegistrationForm
from app.models.user import User
from app import db, login_manager
import uuid
import redis
from app.config.config import Config
from urllib.parse import urlparse
import logging
from app.utils.api_error_handler import api_error_handler

auth = Blueprint('auth', __name__)
auth_service = AuthService()
redis_service = RedisService()

# Инициализация Redis
redis_client = redis.Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=Config.REDIS_DB,
    decode_responses=True
)

@auth.route('/register', methods=['GET', 'POST'])
@api_error_handler
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.chat'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(
                email=form.email.data,
                is_active=True
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Поздравляем, вы успешно зарегистрировались!', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Ошибка при регистрации: {str(e)}")
            flash('Произошла ошибка при регистрации. Попробуйте позже.', 'error')
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
@api_error_handler
def login():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('main.chat'))

        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                logging.info(f"Пользователь найден: {user.email}")
            else:
                logging.warning(f"Пользователь с email {form.email.data} не найден.")

            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                flash('Вы успешно вошли в систему!', 'success')
                return redirect(url_for('main.chat'))
            flash('Неверный email или пароль.', 'error')

        return render_template('auth/login.html', form=form)
    except Exception as e:
        logging.error(f"Ошибка в маршруте /login: {e}")
        return render_template('500.html'), 500

@auth.route('/logout')
@api_error_handler
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/profile')
@login_required
@api_error_handler
def profile():
    return render_template('auth/profile.html', user=current_user)