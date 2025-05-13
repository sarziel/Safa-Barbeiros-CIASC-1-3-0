from app import create_app
from app.models.models import Admin
from app import db
import secrets
import uuid

# Criar aplicação Flask
app = create_app()

# Criar um administrador padrão
with app.app_context():
    # Verificar se já existe um administrador
    if not Admin.query.first():
        # Gerar um ID único
        admin_id = str(uuid.uuid4())
        
        # Criar o administrador
        admin = Admin(
            id=admin_id,
            nome="Administrador",
            username="admin",
            email="admin@safabarbeiros.com",
            tipo="admin"
        )
        
        # Definir senha
        senha = "admin123"
        admin.set_password(senha)
        
        # Adicionar ao banco de dados
        db.session.add(admin)
        db.session.commit()
        
        print(f"Administrador criado com sucesso!")
        print(f"Nome de usuário: admin")
        print(f"Senha: {senha}")
    else:
        print("Já existe um administrador no sistema.")