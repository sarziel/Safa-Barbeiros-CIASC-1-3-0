import os
import logging
from flask import Flask
from flask_login import LoginManager
from pymongo import MongoClient

# Configuração básica de logging
logging.basicConfig(level=logging.DEBUG)

# Inicialização do cliente MongoDB
mongodb = MongoClient("mongodb://mongo:UZOJNpqtUdDKjRHawTQJByTFPBUwTKvL@switchback.proxy.rlwy.net:23885")
db = mongodb['safabarbeiros']  # Define o nome do banco de dados

# Criar as coleções necessárias se não existirem
db.users.create_index([('email', 1)], unique=True)
db.users.create_index([('username', 1)], unique=True)

# Inicialização do LoginManager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Faça login para acessar esta página'
login_manager.login_message_category = 'warning'

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "safabarbeiros-dev-key")

    # Configurações para upload de arquivos
    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Inicialização do login manager
    login_manager.init_app(app)

    # Importação dos modelos
    from app.models.models import User

    # Função para carregar o usuário para o Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    # Registro dos blueprints
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.barbeiro import barbeiro_bp
    from app.routes.cliente import cliente_bp
    from app.routes.common import common_bp
    from app.routes.replit_auth import replit_auth_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(barbeiro_bp, url_prefix='/barbeiro')
    app.register_blueprint(cliente_bp, url_prefix='/cliente')
    app.register_blueprint(common_bp)
    app.register_blueprint(replit_auth_bp, url_prefix='/auth')

    return app