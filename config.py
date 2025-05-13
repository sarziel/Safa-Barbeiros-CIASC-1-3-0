import os

class Config:
    """Classe base de configuração"""
    # Configuração do Flask
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'safabarbeiros-dev-key')
    DEBUG = False
    TESTING = False
    
    # Configuração do MongoDB
    MONGODB_URI = os.environ.get('DATABASE_URL', 'mongodb://mongo:UZOJNpqtUdDKjRHawTQJByTFPBUwTKvL@switchback.proxy.rlwy.net:23885')
    
    # Configuração para upload de arquivos
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')

class DevelopmentConfig(Config):
    """Configuração para ambiente de desenvolvimento"""
    DEBUG = True
    
class TestingConfig(Config):
    """Configuração para ambiente de testes"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
class ProductionConfig(Config):
    """Configuração para ambiente de produção"""
    DEBUG = False
    TESTING = False
    
    # Em produção, garantir que o SECRET_KEY esteja definido no ambiente
    SECRET_KEY = os.environ.get('SESSION_SECRET')
    
    # Configuração de segurança adicional
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora

# Dicionário com as configurações disponíveis
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
