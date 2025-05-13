
from app import create_app, db
from app.models.models import User, Cliente, Barbeiro, Admin, Agendamento, HorarioDisponivel, Venda, Permissao
from werkzeug.security import generate_password_hash
from datetime import datetime

def migrate_database():
    app = create_app()
    with app.app_context():
        # Criar índices únicos
        db.users.create_index([('email', 1)], unique=True)
        db.users.create_index([('username', 1)], unique=True)
        
        # Criar admin padrão se não existir
        if not db.users.find_one({'username': 'admin'}):
            admin = Admin(
                username='admin',
                nome='Administrador',
                email='admin@example.com',
                senha_hash=generate_password_hash('admin123'),
                tipo='admin'
            )
            admin.save()
            print("Admin criado com sucesso!")
        
        print("Migração concluída!")

if __name__ == '__main__':
    migrate_database()
