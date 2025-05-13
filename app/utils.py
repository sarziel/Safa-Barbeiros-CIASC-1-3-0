import os
from datetime import datetime
import uuid
from functools import wraps

from flask import flash, redirect, url_for, current_app
from flask_login import current_user
from werkzeug.utils import secure_filename


# Decorador para verificar se o usuário é administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.tipo != 'admin':
            flash('Acesso negado. Você precisa ser um administrador para acessar esta página.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


# Decorador para verificar se o usuário é barbeiro
def barbeiro_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.tipo != 'barbeiro':
            flash('Acesso negado. Você precisa ser um barbeiro para acessar esta página.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


# Decorador para verificar se o usuário é cliente
def cliente_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.tipo != 'cliente':
            flash('Acesso negado. Você precisa ser um cliente para acessar esta página.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


# Função para verificar se a extensão do arquivo é permitida
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Função para salvar imagem de perfil
def save_picture(picture_file):
    from flask import current_app
    filename = secure_filename(picture_file.filename)
    picture_file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    return filename


# Funções de utilidade para templates
def now():
    return datetime.now()


def get_db():
    from app import db
    return db


def inject_now():
    return {'now': now}