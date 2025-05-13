import os
from app import create_app
from app.utils import inject_now

# Cria a aplicação Flask
app = create_app()

# Registra funções de utilidade no contexto do template
app.context_processor(inject_now)

if __name__ == '__main__':
    # Define a porta padrão como 5000 para desenvolvimento local
    port = int(os.environ.get('PORT', 5000))
    
    # Executa a aplicação
    app.run(host='0.0.0.0', port=port, debug=True)
