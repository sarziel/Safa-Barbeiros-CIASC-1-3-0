from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.models import Cliente, Barbeiro, Agendamento, HorarioDisponivel
from app.utils import cliente_required

cliente_bp = Blueprint('cliente', __name__)

@cliente_bp.route('/dashboard')
@login_required
@cliente_required
def dashboard():
    # Listar todos os barbeiros ativos
    barbeiros_ativos = Barbeiro.query.filter_by(ativo=True).order_by(Barbeiro.nome).all()
    
    # Agendamentos futuros do cliente
    agendamentos_futuros = Agendamento.query.filter(
        Agendamento.cliente_id == current_user.id,
        Agendamento.status == 'agendado',
        Agendamento.data_hora >= datetime.now()
    ).order_by(Agendamento.data_hora).all()
    
    return render_template('cliente/dashboard.html',
                          barbeiros=barbeiros_ativos,
                          agendamentos=agendamentos_futuros)

@cliente_bp.route('/barbeiros/<int:barbeiro_id>/horarios')
@login_required
@cliente_required
def horarios_barbeiro(barbeiro_id):
    barbeiro = Barbeiro.query.get_or_404(barbeiro_id)
    
    # Verificar se o barbeiro está ativo
    if not barbeiro.ativo:
        flash('Este barbeiro não está disponível no momento.', 'warning')
        return redirect(url_for('cliente.dashboard'))
    
    # Obter horários disponíveis do barbeiro
    horarios = HorarioDisponivel.query.filter_by(barbeiro_id=barbeiro_id).order_by(
        HorarioDisponivel.dia_semana,
        HorarioDisponivel.hora_inicio
    ).all()
    
    # Criar agenda para os próximos 7 dias
    hoje = datetime.now().date()
    agenda = []
    dias_semana = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
    
    for i in range(7):
        data = hoje + timedelta(days=i)
        dia_semana_idx = data.weekday()  # 0 = Segunda, 6 = Domingo
        
        # Filtrar horários disponíveis para este dia da semana
        horarios_dia = [h for h in horarios if h.dia_semana == dia_semana_idx]
        
        # Verificar quais horários já estão agendados
        slots_disponiveis = []
        for horario in horarios_dia:
            # Criar slots de 30 minutos
            hora_atual = datetime.combine(data, horario.hora_inicio)
            hora_fim = datetime.combine(data, horario.hora_fim)
            
            while hora_atual < hora_fim:
                # Verificar se este slot já está agendado
                agendamento_existente = Agendamento.query.filter(
                    Agendamento.barbeiro_id == barbeiro_id,
                    Agendamento.data_hora == hora_atual,
                    Agendamento.status == 'agendado'
                ).first()
                
                if not agendamento_existente:
                    slots_disponiveis.append({
                        'hora': hora_atual,
                        'hora_formatada': hora_atual.strftime('%H:%M')
                    })
                
                # Avançar para o próximo slot de 30 minutos
                hora_atual += timedelta(minutes=30)
        
        agenda.append({
            'data': data,
            'data_formatada': data.strftime('%d/%m/%Y'),
            'dia_semana': dias_semana[dia_semana_idx],
            'slots': slots_disponiveis
        })
    
    return render_template('cliente/horarios_barbeiro.html',
                          barbeiro=barbeiro,
                          agenda=agenda)

@cliente_bp.route('/agendar', methods=['POST'])
@login_required
@cliente_required
def agendar():
    barbeiro_id = request.form.get('barbeiro_id', type=int)
    data_hora_str = request.form.get('data_hora')
    
    # Validações
    if not barbeiro_id or not data_hora_str:
        flash('Dados inválidos para agendamento!', 'danger')
        return redirect(url_for('cliente.dashboard'))
    
    barbeiro = Barbeiro.query.get_or_404(barbeiro_id)
    
    # Verificar se o barbeiro está ativo
    if not barbeiro.ativo:
        flash('Este barbeiro não está disponível para agendamentos.', 'warning')
        return redirect(url_for('cliente.dashboard'))
    
    try:
        data_hora = datetime.strptime(data_hora_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        flash('Formato de data/hora inválido!', 'danger')
        return redirect(url_for('cliente.horarios_barbeiro', barbeiro_id=barbeiro_id))
    
    # Verificar se o horário já passou
    if data_hora < datetime.now():
        flash('Não é possível agendar para uma data/hora passada!', 'danger')
        return redirect(url_for('cliente.horarios_barbeiro', barbeiro_id=barbeiro_id))
    
    # Verificar se o horário já está agendado
    agendamento_existente = Agendamento.query.filter(
        Agendamento.barbeiro_id == barbeiro_id,
        Agendamento.data_hora == data_hora,
        Agendamento.status == 'agendado'
    ).first()
    
    if agendamento_existente:
        flash('Este horário já está agendado. Por favor, selecione outro.', 'danger')
        return redirect(url_for('cliente.horarios_barbeiro', barbeiro_id=barbeiro_id))
    
    # Verificar se o dia e horário está na disponibilidade do barbeiro
    dia_semana = data_hora.weekday()
    hora = data_hora.time()
    
    horario_disponivel = HorarioDisponivel.query.filter(
        HorarioDisponivel.barbeiro_id == barbeiro_id,
        HorarioDisponivel.dia_semana == dia_semana,
        HorarioDisponivel.hora_inicio <= hora,
        HorarioDisponivel.hora_fim >= hora
    ).first()
    
    if not horario_disponivel:
        flash('Este horário não está disponível para agendamento!', 'danger')
        return redirect(url_for('cliente.horarios_barbeiro', barbeiro_id=barbeiro_id))
    
    # Criar novo agendamento
    novo_agendamento = Agendamento(
        cliente_id=current_user.id,
        barbeiro_id=barbeiro_id,
        data_hora=data_hora,
        status='agendado'
    )
    
    db.session.add(novo_agendamento)
    db.session.commit()
    
    flash('Agendamento realizado com sucesso!', 'success')
    return redirect(url_for('cliente.agendamentos'))

@cliente_bp.route('/agendamentos')
@login_required
@cliente_required
def agendamentos():
    # Paginação
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Filtragem por status
    status_filtro = request.args.get('status', 'todos')
    
    # Consulta base
    query = Agendamento.query.filter_by(cliente_id=current_user.id)
    
    # Aplicar filtro de status se necessário
    if status_filtro != 'todos':
        query = query.filter_by(status=status_filtro)
    
    # Ordenar por data e hora (mais recentes primeiro)
    query = query.order_by(Agendamento.data_hora.desc())
    
    # Paginar resultados
    agendamentos_paginados = query.paginate(page=page, per_page=per_page)
    
    return render_template('cliente/agendamentos.html',
                          agendamentos=agendamentos_paginados,
                          status_filtro=status_filtro)

@cliente_bp.route('/agendamentos/<int:agendamento_id>/cancelar', methods=['POST'])
@login_required
@cliente_required
def cancelar_agendamento(agendamento_id):
    agendamento = Agendamento.query.get_or_404(agendamento_id)
    
    # Verificar se o agendamento pertence ao cliente atual
    if agendamento.cliente_id != current_user.id:
        flash('Acesso negado!', 'danger')
        return redirect(url_for('cliente.agendamentos'))
    
    # Verificar se o agendamento já foi cancelado ou concluído
    if agendamento.status != 'agendado':
        flash('Este agendamento não pode ser cancelado!', 'warning')
        return redirect(url_for('cliente.agendamentos'))
    
    # Verificar se o agendamento é para uma data futura (pelo menos 1 hora antes)
    if agendamento.data_hora <= (datetime.now() + timedelta(hours=1)):
        flash('Agendamentos só podem ser cancelados com pelo menos 1 hora de antecedência!', 'danger')
        return redirect(url_for('cliente.agendamentos'))
    
    # Cancelar o agendamento
    agendamento.status = 'cancelado'
    db.session.commit()
    
    flash('Agendamento cancelado com sucesso!', 'success')
    return redirect(url_for('cliente.agendamentos'))
