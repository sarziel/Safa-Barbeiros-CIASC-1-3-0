
from app import create_app, db
from app.models.models import User, Cliente, Barbeiro, Admin, Agendamento, HorarioDisponivel, Venda, Permissao, OAuth

app = create_app()

def check_database():
    with app.app_context():
        # Verificar conexão
        try:
            # Listar todas as tabelas
            print("\n=== Tabelas no banco de dados ===")
            for table in db.metadata.tables.keys():
                print(f"- {table}")
            
            # Contagem de registros
            print("\n=== Contagem de registros ===")
            print(f"Usuários: {User.query.count()}")
            print(f"Clientes: {Cliente.query.count()}")
            print(f"Barbeiros: {Barbeiro.query.count()}")
            print(f"Admins: {Admin.query.count()}")
            print(f"Agendamentos: {Agendamento.query.count()}")
            print(f"Horários Disponíveis: {HorarioDisponivel.query.count()}")
            print(f"Vendas: {Venda.query.count()}")
            print(f"Permissões: {Permissao.query.count()}")
            print(f"OAuth: {OAuth.query.count()}")
            
            print("\nConexão com o banco de dados está funcionando!")
            
        except Exception as e:
            print(f"\nErro ao conectar com o banco de dados: {str(e)}")

if __name__ == "__main__":
    check_database()
