from app import create_app
from app.models.models import Admin
from werkzeug.security import generate_password_hash

def setup_admin():
    app = create_app()
    with app.app_context():
        admin = Admin(
            username='admin',
            nome='Administrador',
            email='admin@example.com',
            senha_hash=generate_password_hash('admin123'),
            tipo='admin'
        )
        admin.save()
        print("Admin user created successfully!")

if __name__ == '__main__':
    setup_admin()