import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase

# Configuração básica de logging
logging.basicConfig(level=logging.DEBUG)

# Configuração da base declarativa para o SQLAlchemy
class Base(DeclarativeBase):
    pass

# Inicialização da extensão do SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Inicialização do LoginManager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Faça login para acessar esta página'
login_manager.login_message_category = 'warning'

def create_app():
    # Criação da instância do Flask
    app = Flask(__name__)
    
    # Configuração do secret key
    app.secret_key = os.environ.get("SESSION_SECRET", "safabarbeiros-dev-key")
    
    # Configuração da conexão com o banco de dados
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", 
                                          "mysql://root:YDZtCgcxrhTHrpmpVunCpgdabUEZkKQc@trolley.proxy.rlwy.net:40848/railway")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Configurações para upload de arquivos
    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
    
    # Cria a pasta de uploads se não existir
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Inicialização das extensões
    db.init_app(app)
    login_manager.init_app(app)
    
    # Importação dos modelos
    from app.models.models import User, Cliente, Barbeiro, Admin
    
    # Função para carregar o usuário para o Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
    
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
    
    # Criação das tabelas do banco de dados
    with app.app_context():
        db.create_all()
    
    return app
