from app import create_app, db

def check_database():
    app = create_app()
    with app.app_context():
        try:
            # Verificar conexão
            collections = db.list_collection_names()

            print("\n=== Status do MongoDB ===")
            print("Conexão: OK")
            print("\n=== Coleções ===")
            for collection in collections:
                count = db[collection].count_documents({})
                print(f"{collection}: {count} documentos")

        except Exception as e:
            print(f"\nErro na conexão: {str(e)}")

if __name__ == "__main__":
    check_database()