from datetime import datetime
from bson import ObjectId
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self, **kwargs):
        self._id = kwargs.get('_id', ObjectId())
        self.id = str(self._id)
        self.nome = kwargs.get('nome')
        self.username = kwargs.get('username')
        self.email = kwargs.get('email')
        self.senha_hash = kwargs.get('senha_hash')
        self.tipo = kwargs.get('tipo', 'cliente')
        self.foto_perfil = kwargs.get('foto_perfil', 'default.jpg')
        self.data_criacao = kwargs.get('data_criacao', datetime.utcnow())

    @staticmethod
    def get(user_id):
        from app import db
        if isinstance(user_id, str):
            if len(user_id) == 24:
                user_id = ObjectId(user_id)
            user_data = db.users.find_one({'_id': user_id})
            return User(**user_data) if user_data else None
        return None

    def save(self):
        from app import db
        data = {
            'nome': self.nome,
            'username': self.username,
            'email': self.email,
            'senha_hash': self.senha_hash,
            'tipo': self.tipo,
            'foto_perfil': self.foto_perfil,
            'data_criacao': self.data_criacao
        }
        if hasattr(self, '_id'):
            db.users.update_one({'_id': self._id}, {'$set': data})
        else:
            result = db.users.insert_one(data)
            self._id = result.inserted_id
            self.id = str(self._id)

    def set_password(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_password(self, senha):
        return check_password_hash(self.senha_hash, senha)

class Cliente(User):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.numero_aluno = kwargs.get('numero_aluno')
        self.tipo = 'cliente'

    def save(self):
        data = {
            'nome': self.nome,
            'username': self.username,
            'email': self.email,
            'senha_hash': self.senha_hash,
            'tipo': self.tipo,
            'foto_perfil': self.foto_perfil,
            'data_criacao': self.data_criacao,
            'numero_aluno': self.numero_aluno
        }
        from app import db
        if hasattr(self, '_id'):
            db.users.update_one({'_id': self._id}, {'$set': data})
        else:
            result = db.users.insert_one(data)
            self._id = result.inserted_id
            self.id = str(self._id)

class Barbeiro(User):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.numero_aluno = kwargs.get('numero_aluno')
        self.ativo = kwargs.get('ativo', False)
        self.tipo = 'barbeiro'

    def save(self):
        data = {
            'nome': self.nome,
            'username': self.username,
            'email': self.email,
            'senha_hash': self.senha_hash,
            'tipo': self.tipo,
            'foto_perfil': self.foto_perfil,
            'data_criacao': self.data_criacao,
            'numero_aluno': self.numero_aluno,
            'ativo': self.ativo
        }
        from app import db
        if hasattr(self, '_id'):
            db.users.update_one({'_id': self._id}, {'$set': data})
        else:
            result = db.users.insert_one(data)
            self._id = result.inserted_id
            self.id = str(self._id)

class Admin(User):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tipo = 'admin'

    def save(self):
        data = {
            'nome': self.nome,
            'username': self.username,
            'email': self.email,
            'senha_hash': self.senha_hash,
            'tipo': self.tipo,
            'foto_perfil': self.foto_perfil,
            'data_criacao': self.data_criacao
        }
        from app import db
        if hasattr(self, '_id'):
            db.users.update_one({'_id': self._id}, {'$set': data})
        else:
            result = db.users.insert_one(data)
            self._id = result.inserted_id
            self.id = str(self._id)

class Agendamento:
    def __init__(self, **kwargs):
        self._id = kwargs.get('_id', ObjectId())
        self.id = str(self._id)
        self.cliente_id = kwargs.get('cliente_id')
        self.barbeiro_id = kwargs.get('barbeiro_id')
        self.data_hora = kwargs.get('data_hora')
        self.status = kwargs.get('status', 'agendado')
        self.data_criacao = kwargs.get('data_criacao', datetime.utcnow())

    def save(self):
        data = {
            'cliente_id': self.cliente_id,
            'barbeiro_id': self.barbeiro_id,
            'data_hora': self.data_hora,
            'status': self.status,
            'data_criacao': self.data_criacao
        }
        from app import db
        if hasattr(self, '_id'):
            db.agendamentos.update_one({'_id': self._id}, {'$set': data})
        else:
            result = db.agendamentos.insert_one(data)
            self._id = result.inserted_id
            self.id = str(self._id)

class HorarioDisponivel:
    def __init__(self, **kwargs):
        self._id = kwargs.get('_id', ObjectId())
        self.id = str(self._id)
        self.barbeiro_id = kwargs.get('barbeiro_id')
        self.dia_semana = kwargs.get('dia_semana')
        self.hora_inicio = kwargs.get('hora_inicio')
        self.hora_fim = kwargs.get('hora_fim')
        self.data_criacao = kwargs.get('data_criacao', datetime.utcnow())

    def save(self):
        data = {
            'barbeiro_id': self.barbeiro_id,
            'dia_semana': self.dia_semana,
            'hora_inicio': self.hora_inicio,
            'hora_fim': self.hora_fim,
            'data_criacao': self.data_criacao
        }
        from app import db
        if hasattr(self, '_id'):
            db.horarios_disponiveis.update_one({'_id': self._id}, {'$set': data})
        else:
            result = db.horarios_disponiveis.insert_one(data)
            self._id = result.inserted_id
            self.id = str(self._id)

class Venda:
    def __init__(self, **kwargs):
        self._id = kwargs.get('_id', ObjectId())
        self.id = str(self._id)
        self.barbeiro_id = kwargs.get('barbeiro_id')
        self.cliente_id = kwargs.get('cliente_id')
        self.valor = kwargs.get('valor')
        self.data = kwargs.get('data', datetime.utcnow())
        self.descricao = kwargs.get('descricao')
        self.tipo = kwargs.get('tipo', 'normal')
        self.data_criacao = kwargs.get('data_criacao', datetime.utcnow())

    def save(self):
        data = {
            'barbeiro_id': self.barbeiro_id,
            'cliente_id': self.cliente_id,
            'valor': self.valor,
            'data': self.data,
            'descricao': self.descricao,
            'tipo': self.tipo,
            'data_criacao': self.data_criacao
        }
        from app import db
        if hasattr(self, '_id'):
            db.vendas.update_one({'_id': self._id}, {'$set': data})
        else:
            result = db.vendas.insert_one(data)
            self._id = result.inserted_id
            self.id = str(self._id)

class Permissao:
    def __init__(self, **kwargs):
        self._id = kwargs.get('_id', ObjectId())
        self.id = str(self._id)
        self.barbeiro_id = kwargs.get('barbeiro_id')
        self.ativo = kwargs.get('ativo', False)
        self.data_criacao = kwargs.get('data_criacao', datetime.utcnow())
        self.data_modificacao = kwargs.get('data_modificacao')

    def save(self):
        data = {
            'barbeiro_id': self.barbeiro_id,
            'ativo': self.ativo,
            'data_criacao': self.data_criacao,
            'data_modificacao': datetime.utcnow()
        }
        from app import db
        if hasattr(self, '_id'):
            db.permissoes.update_one({'_id': self._id}, {'$set': data})
        else:
            result = db.permissoes.insert_one(data)
            self._id = result.inserted_id
            self.id = str(self._id)