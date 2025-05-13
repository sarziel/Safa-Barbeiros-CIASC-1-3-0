
from app import create_app
from app.models.models import User, Cliente, Barbeiro, Admin
import os

def check_deployment_readiness():
    app = create_app()
    
    checks = {
        "DATABASE_URL": bool(os.environ.get("DATABASE_URL")),
        "SESSION_SECRET": bool(os.environ.get("SESSION_SECRET")),
        "UPLOAD_FOLDER": os.path.exists(app.config["UPLOAD_FOLDER"]),
        "DATABASE_MODELS": all(m.__table__.exists(m.query.session.bind) 
                             for m in [User, Cliente, Barbeiro, Admin])
    }
    
    print("\n=== Verificação de Deploy ===")
    for check, status in checks.items():
        print(f"{check}: {'✓' if status else '✗'}")
    
    return all(checks.values())

if __name__ == "__main__":
    is_ready = check_deployment_readiness()
    print(f"\nStatus: {'Pronto para deploy!' if is_ready else 'Ajustes necessários!'}")
