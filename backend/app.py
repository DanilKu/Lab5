from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import sqlite3
import os
import re

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
CORS(app)
jwt = JWTManager(app)

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            email VARCHAR(150) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(50) DEFAULT 'user',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Валидация email
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Валидация пароля
def validate_password(password):
    if len(password) < 6:
        return False, "Пароль должен содержать минимум 6 символов"
    return True, ""

# Регистрация пользователя
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Валидация данных
        if not data:
            return jsonify({'error': 'Данные не предоставлены'}), 400
        
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Проверка обязательных полей
        if not first_name:
            return jsonify({'error': 'Имя обязательно для заполнения'}), 400
        if not last_name:
            return jsonify({'error': 'Фамилия обязательна для заполнения'}), 400
        if not email:
            return jsonify({'error': 'Email обязателен для заполнения'}), 400
        if not password:
            return jsonify({'error': 'Пароль обязателен для заполнения'}), 400
        
        # Валидация email
        if not validate_email(email):
            return jsonify({'error': 'Некорректный формат email'}), 400
        
        # Валидация пароля
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Проверка существования пользователя
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Пользователь с таким email уже существует'}), 400
        
        # Хэширование пароля
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        
        # Сохранение пользователя
        cursor.execute('''
            INSERT INTO users (first_name, last_name, email, password, role)
            VALUES (?, ?, ?, ?, ?)
        ''', (first_name, last_name, email, password_hash, 'user'))
        
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'message': 'Регистрация успешна',
            'user_id': user_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500

# Вход пользователя
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Данные не предоставлены'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email и пароль обязательны для заполнения'}), 400
        
        # Поиск пользователя
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, first_name, last_name, email, password, role FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({'error': 'Неверный email или пароль'}), 401
        
        user_id, first_name, last_name, user_email, password_hash, role = user
        
        # Проверка пароля
        if not check_password_hash(password_hash, password):
            return jsonify({'error': 'Неверный email или пароль'}), 401
        
        # Генерация JWT токена
        access_token = create_access_token(
            identity=user_id,
            additional_claims={'email': user_email, 'role': role}
        )
        
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user_id,
                'first_name': first_name,
                'last_name': last_name,
                'email': user_email,
                'role': role
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500

# Получение информации о текущем пользователе
@app.route('/api/user', methods=['GET'])
@jwt_required()
def get_user():
    try:
        user_id = get_jwt_identity()
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, first_name, last_name, email, role, created_at
            FROM users WHERE id = ?
        ''', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({'error': 'Пользователь не найден'}), 404
        
        return jsonify({
            'id': user[0],
            'first_name': user[1],
            'last_name': user[2],
            'email': user[3],
            'role': user[4],
            'created_at': user[5]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500

# Выход пользователя
@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({'message': 'Выход выполнен успешно'}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)

