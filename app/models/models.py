from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

# Definição da tabela de usuários
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)  # Email pode ser nulo para alguns métodos de login
    senha_hash = db.Column(db.String(256), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    foto_perfil = db.Column(db.String(255), default='default.jpg')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    __mapper_args__ = {
        'polymorphic_on': tipo,
        'polymorphic_identity': 'user'
    }
    
    def set_password(self, senha):
        self.senha_hash = generate_password_hash(senha)
        
    def check_password(self, senha):
        return check_password_hash(self.senha_hash, senha)

# Modelo para Cliente
class Cliente(User):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    numero_aluno = db.Column(db.String(4), nullable=True)
    
    # Relacionamentos
    agendamentos = db.relationship('Agendamento', backref='cliente', lazy='dynamic')
    vendas = db.relationship('Venda', backref='cliente', lazy='dynamic')
    
    __mapper_args__ = {
        'polymorphic_identity': 'cliente'
    }

# Modelo para Barbeiro
class Barbeiro(User):
    __tablename__ = 'barbeiros'
    
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    numero_aluno = db.Column(db.String(4), nullable=True)
    ativo = db.Column(db.Boolean, default=False)
    
    # Relacionamentos
    horarios_disponiveis = db.relationship('HorarioDisponivel', backref='barbeiro', lazy='dynamic')
    agendamentos = db.relationship('Agendamento', backref='barbeiro', lazy='dynamic')
    vendas = db.relationship('Venda', backref='barbeiro', lazy='dynamic')
    permissao = db.relationship('Permissao', backref='barbeiro', uselist=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'barbeiro'
    }

# Modelo para Administrador
class Admin(User):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'admin'
    }

# Modelo para Agendamentos
class Agendamento(db.Model):
    __tablename__ = 'agendamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    barbeiro_id = db.Column(db.Integer, db.ForeignKey('barbeiros.id'), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='agendado')  # agendado, concluido, cancelado
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

# Modelo para Horários Disponíveis
class HorarioDisponivel(db.Model):
    __tablename__ = 'horarios_disponiveis'
    
    id = db.Column(db.Integer, primary_key=True)
    barbeiro_id = db.Column(db.Integer, db.ForeignKey('barbeiros.id'), nullable=False)
    dia_semana = db.Column(db.Integer, nullable=False)  # 0-6 (Segunda a Domingo)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

# Modelo para Vendas
class Venda(db.Model):
    __tablename__ = 'vendas'
    
    id = db.Column(db.Integer, primary_key=True)
    barbeiro_id = db.Column(db.Integer, db.ForeignKey('barbeiros.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True)  # Nullable para venda fiada
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    descricao = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(20), default='normal')  # normal, fiada
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

# Modelo para Permissões
class Permissao(db.Model):
    __tablename__ = 'permissoes'
    
    id = db.Column(db.Integer, primary_key=True)
    barbeiro_id = db.Column(db.Integer, db.ForeignKey('barbeiros.id'), nullable=False)
    ativo = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_modificacao = db.Column(db.DateTime, onupdate=datetime.utcnow)
