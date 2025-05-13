from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.models import Barbeiro, Cliente, Agendamento, HorarioDisponivel, Venda
from app.utils import barbeiro_required

barbeiro_bp = Blueprint('barbeiro', __name__)

@barbeiro_bp.route('/dashboard')
@login_required
@barbeiro_required
def dashboard():
    # Obtém o barbeiro atual
    barbeiro = Barbeiro.query.get(current_user.id)
    
    # Verifica se o barbeiro está ativo
    if not barbeiro.ativo:
        flash('Sua conta está desativada. Entre em contato com o administrador.', 'warning')
        return redirect(url_for('auth.logout'))
    
    # Dados para o dashboard financeiro
    hoje = datetime.now().date()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    inicio_mes = hoje.replace(day=1)
    
    # Vendas de hoje
    vendas_hoje = Venda.query.filter(
        Venda.barbeiro_id == current_user.id,
        Venda.data >= datetime.combine(hoje, datetime.min.time()),
        Venda.data <= datetime.combine(hoje, datetime.max.time())
    ).all()
    
    valor_vendas_hoje = sum(venda.valor for venda in vendas_hoje)
    
    # Vendas da semana
    vendas_semana = Venda.query.filter(
        Venda.barbeiro_id == current_user.id,
        Venda.data >= datetime.combine(inicio_semana, datetime.min.time())
    ).all()
    
    valor_vendas_semana = sum(venda.valor for venda in vendas_semana)
    
    # Vendas do mês
    vendas_mes = Venda.query.filter(
        Venda.barbeiro_id == current_user.id,
        Venda.data >= datetime.combine(inicio_mes, datetime.min.time())
    ).all()
    
    valor_vendas_mes = sum(venda.valor for venda in vendas_mes)
    
    # Vendas fiadas
    vendas_fiadas = Venda.query.filter(
        Venda.barbeiro_id == current_user.id,
        Venda.tipo == 'fiada'
    ).all()
    
    valor_vendas_fiadas = sum(venda.valor for venda in vendas_fiadas)
    
    # Agendamentos do dia
    agendamentos_hoje = Agendamento.query.filter(
        Agendamento.barbeiro_id == current_user.id,
        Agendamento.data_hora >= datetime.combine(hoje, datetime.min.time()),
        Agendamento.data_hora <= datetime.combine(hoje, datetime.max.time())
    ).order_by(Agendamento.data_hora).all()
    
    # Dados para gráfico de vendas por dia da semana (últimos 7 dias)
    dados_grafico = []
    for i in range(6, -1, -1):
        data = hoje - timedelta(days=i)
        vendas_dia = Venda.query.filter(
            Venda.barbeiro_id == current_user.id,
            Venda.data >= datetime.combine(data, datetime.min.time()),
            Venda.data <= datetime.combine(data, datetime.max.time())
        ).all()
        
        valor_dia = sum(venda.valor for venda in vendas_dia)
        dados_grafico.append({
            'data': data.strftime('%d/%m'),
            'valor': valor_dia
        })
    
    return render_template('barbeiro/dashboard.html',
                          vendas_hoje=vendas_hoje,
                          valor_vendas_hoje=valor_vendas_hoje,
                          valor_vendas_semana=valor_vendas_semana,
                          valor_vendas_mes=valor_vendas_mes,
                          valor_vendas_fiadas=valor_vendas_fiadas,
                          agendamentos_hoje=agendamentos_hoje,
                          dados_grafico=dados_grafico)

@barbeiro_bp.route('/horarios', methods=['GET', 'POST'])
@login_required
@barbeiro_required
def horarios():
    if request.method == 'POST':
        dia_semana = request.form.get('dia_semana', type=int)
        hora_inicio = request.form.get('hora_inicio')
        hora_fim = request.form.get('hora_fim')
        
        # Validações
        if not all([dia_semana is not None, hora_inicio, hora_fim]):
            flash('Todos os campos são obrigatórios!', 'danger')
            return redirect(url_for('barbeiro.horarios'))
            
        if dia_semana < 0 or dia_semana > 6:
            flash('Dia da semana inválido!', 'danger')
            return redirect(url_for('barbeiro.horarios'))
        
        # Converter strings para objetos time
        try:
            hora_inicio_obj = datetime.strptime(hora_inicio, '%H:%M').time()
            hora_fim_obj = datetime.strptime(hora_fim, '%H:%M').time()
        except ValueError:
            flash('Formato de hora inválido!', 'danger')
            return redirect(url_for('barbeiro.horarios'))
            
        if hora_inicio_obj >= hora_fim_obj:
            flash('A hora de início deve ser anterior à hora de fim!', 'danger')
            return redirect(url_for('barbeiro.horarios'))
        
        # Verificar conflito com horários existentes
        horarios_existentes = HorarioDisponivel.query.filter_by(
            barbeiro_id=current_user.id,
            dia_semana=dia_semana
        ).all()
        
        for horario in horarios_existentes:
            if (hora_inicio_obj < horario.hora_fim and hora_fim_obj > horario.hora_inicio):
                flash('Este horário conflita com outro já cadastrado!', 'danger')
                return redirect(url_for('barbeiro.horarios'))
        
        # Criar novo horário disponível
        novo_horario = HorarioDisponivel(
            barbeiro_id=current_user.id,
            dia_semana=dia_semana,
            hora_inicio=hora_inicio_obj,
            hora_fim=hora_fim_obj
        )
        
        db.session.add(novo_horario)
        db.session.commit()
        
        flash('Horário adicionado com sucesso!', 'success')
        return redirect(url_for('barbeiro.horarios'))
    
    # Obter todos os horários disponíveis do barbeiro
    horarios_barbeiro = HorarioDisponivel.query.filter_by(barbeiro_id=current_user.id).order_by(
        HorarioDisponivel.dia_semana,
        HorarioDisponivel.hora_inicio
    ).all()
    
    # Nomes dos dias da semana
    dias_semana = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
    
    return render_template('barbeiro/horarios.html', 
                          horarios=horarios_barbeiro,
                          dias_semana=dias_semana)

@barbeiro_bp.route('/horarios/<string:horario_id>/excluir', methods=['POST'])
@login_required
@barbeiro_required
def excluir_horario(horario_id):
    horario = HorarioDisponivel.query.get_or_404(horario_id)
    
    # Verificar se o horário pertence ao barbeiro atual
    if horario.barbeiro_id != current_user.id:
        flash('Acesso negado!', 'danger')
        return redirect(url_for('barbeiro.horarios'))
    
    # Verificar se existem agendamentos para este horário
    hoje = datetime.now().date()
    dia_semana = horario.dia_semana
    
    # Encontrar a próxima data com este dia da semana
    dias_a_adicionar = (dia_semana - hoje.weekday()) % 7
    proxima_data = hoje + timedelta(days=dias_a_adicionar)
    
    # Verificar agendamentos futuros neste horário
    agendamentos = Agendamento.query.filter(
        Agendamento.barbeiro_id == current_user.id,
        Agendamento.data_hora >= datetime.combine(proxima_data, horario.hora_inicio),
        Agendamento.data_hora <= datetime.combine(proxima_data, horario.hora_fim),
        Agendamento.status == 'agendado'
    ).all()
    
    if agendamentos:
        flash('Não é possível excluir este horário pois existem agendamentos pendentes!', 'danger')
        return redirect(url_for('barbeiro.horarios'))
    
    db.session.delete(horario)
    db.session.commit()
    
    flash('Horário excluído com sucesso!', 'success')
    return redirect(url_for('barbeiro.horarios'))

@barbeiro_bp.route('/vendas', methods=['GET', 'POST'])
@login_required
@barbeiro_required
def vendas():
    if request.method == 'POST':
        valor = request.form.get('valor', type=float)
        descricao = request.form.get('descricao')
        tipo = request.form.get('tipo', 'normal')
        cliente_id = request.form.get('cliente_id')
        
        # Validações
        if not valor or valor <= 0:
            flash('O valor deve ser maior que zero!', 'danger')
            return redirect(url_for('barbeiro.vendas'))
            
        if not descricao:
            flash('A descrição é obrigatória!', 'danger')
            return redirect(url_for('barbeiro.vendas'))
            
        # Para venda fiada, o cliente é obrigatório
        if tipo == 'fiada' and not cliente_id:
            flash('Selecione um cliente para venda fiada!', 'danger')
            return redirect(url_for('barbeiro.vendas'))
            
        # Verifica se o cliente existe
        if cliente_id:
            cliente = Cliente.query.get(cliente_id)
            if not cliente:
                flash('Cliente não encontrado!', 'danger')
                return redirect(url_for('barbeiro.vendas'))
        else:
            cliente_id = None
        
        # Criar nova venda
        nova_venda = Venda(
            barbeiro_id=current_user.id,
            cliente_id=cliente_id,
            valor=valor,
            descricao=descricao,
            tipo=tipo,
            data=datetime.now()
        )
        
        db.session.add(nova_venda)
        db.session.commit()
        
        if tipo == 'fiada':
            flash('Venda fiada registrada com sucesso!', 'success')
        else:
            flash('Venda registrada com sucesso!', 'success')
            
        return redirect(url_for('barbeiro.vendas'))
    
    # Paginação para listagem de vendas
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    vendas_paginadas = Venda.query.filter_by(barbeiro_id=current_user.id).order_by(
        Venda.data.desc()
    ).paginate(page=page, per_page=per_page)
    
    # Lista de clientes para venda fiada
    clientes = Cliente.query.order_by(Cliente.nome).all()
    
    return render_template('barbeiro/vendas.html',
                          vendas=vendas_paginadas,
                          clientes=clientes)

@barbeiro_bp.route('/agendamentos')
@login_required
@barbeiro_required
def agendamentos():
    # Paginação
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Filtragem por status
    status_filtro = request.args.get('status', 'todos')
    
    # Consulta base
    query = Agendamento.query.filter_by(barbeiro_id=current_user.id)
    
    # Aplicar filtro de status se necessário
    if status_filtro != 'todos':
        query = query.filter_by(status=status_filtro)
    
    # Ordenar por data e hora (mais recentes primeiro)
    query = query.order_by(Agendamento.data_hora.desc())
    
    # Paginar resultados
    agendamentos_paginados = query.paginate(page=page, per_page=per_page)
    
    return render_template('barbeiro/agendamentos.html',
                          agendamentos=agendamentos_paginados,
                          status_filtro=status_filtro)

@barbeiro_bp.route('/agendamentos/<string:agendamento_id>/atualizar', methods=['POST'])
@login_required
@barbeiro_required
def atualizar_agendamento(agendamento_id):
    agendamento = Agendamento.query.get_or_404(agendamento_id)
    
    # Verificar se o agendamento pertence ao barbeiro atual
    if agendamento.barbeiro_id != current_user.id:
        flash('Acesso negado!', 'danger')
        return redirect(url_for('barbeiro.agendamentos'))
    
    novo_status = request.form.get('status')
    
    # Validar o novo status
    if novo_status not in ['agendado', 'concluido', 'cancelado']:
        flash('Status inválido!', 'danger')
        return redirect(url_for('barbeiro.agendamentos'))
    
    agendamento.status = novo_status
    db.session.commit()
    
    flash('Status do agendamento atualizado com sucesso!', 'success')
    return redirect(url_for('barbeiro.agendamentos'))
