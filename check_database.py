
from app import create_app, mongodb

def check_database():
    app = create_app()
    with app.app_context():
        try:
            # Verificar conexão
            db = mongodb.get_database()
            collections = db.list_collection_names()
            
            print("\n=== Coleções no MongoDB ===")
            for collection in collections:
                print(f"- {collection}")
            
            # Contagem de documentos
            print("\n=== Contagem de documentos ===")
            print(f"Usuários: {db.users.count_documents({})}")
            print(f"Clientes: {db.clientes.count_documents({})}")
            print(f"Barbeiros: {db.barbeiros.count_documents({})}")
            print(f"Admins: {db.admins.count_documents({})}")
            print(f"Agendamentos: {db.agendamentos.count_documents({})}")
            print(f"Horários Disponíveis: {db.horarios_disponiveis.count_documents({})}")
            print(f"Vendas: {db.vendas.count_documents({})}")
            
            print("\nConexão com o MongoDB está funcionando!")
            
        except Exception as e:
            print(f"\nErro ao conectar com o MongoDB: {str(e)}")

if __name__ == "__main__":
    check_database()
