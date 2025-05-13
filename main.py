from app import create_app
from app.utils import inject_now

app = create_app()

# Registra funções de utilidade no contexto do template
app.context_processor(inject_now)