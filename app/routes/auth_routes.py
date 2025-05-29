from flask import Blueprint, request, jsonify, render_template
from flask_login import login_user, logout_user, login_required, current_user
from app.services.auth_service import AuthService
from app.services.redis_service import RedisService
import uuid

auth = Blueprint('auth', __name__)
auth_service = AuthService()
redis_service = RedisService()

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('auth/register.html')
        
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    
    if not all([email, username, password]):
        return jsonify({"error": "Все поля обязательны для заполнения"}), 400
        
    success, message = auth_service.register_user(email, username, password)
    
    if success:
        return jsonify({"message": message}), 201
    return jsonify({"error": message}), 400

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
        
    data = request.get_json()
    login = data.get('login')  # email или username
    password = data.get('password')
    
    if not all([login, password]):
        return jsonify({"error": "Все поля обязательны для заполнения"}), 400
        
    success, message, user = auth_service.authenticate_user(
        login, 
        password,
        request.remote_addr
    )
    
    if success and user:
        login_user(user)
        
        # Создаем новую сессию
        session_id = str(uuid.uuid4())
        redis_service.set_user_session(str(user.id), session_id)
        
        return jsonify({
            "message": message,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        })
        
    return jsonify({"error": message}), 401

@auth.route('/logout')
@login_required
def logout():
    user_id = str(current_user.id)
    success, message = auth_service.logout_user(user_id)
    logout_user()
    
    if success:
        return jsonify({"message": message})
    return jsonify({"error": message}), 500

@auth.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', user=current_user) 