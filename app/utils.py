import os
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
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Função para salvar imagem de perfil
def save_picture(file):
    """
    Salva a imagem de perfil do usuário e retorna o nome do arquivo.
    
    Args:
        file: Arquivo de imagem enviado pelo usuário
    
    Returns:
        str: Nome único do arquivo salvo
    """
    # Gera um nome de arquivo único para evitar conflitos
    random_hex = uuid.uuid4().hex
    _, file_ext = os.path.splitext(secure_filename(file.filename))
    picture_filename = random_hex + file_ext
    
    # Define o caminho para salvar o arquivo
    picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], picture_filename)
    
    # Salva o arquivo
    file.save(picture_path)
    
    return picture_filename

from datetime import datetime
from flask import current_app

def now():
    """Returns current datetime for templates"""
    return datetime.now()

def get_db():
    """Get database connection"""
    from app import db
    return db

def inject_now():
    """Inject now function into templates"""
    return dict(now=now)