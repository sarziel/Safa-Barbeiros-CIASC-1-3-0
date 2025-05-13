from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app import db
from app.models.models import User, Cliente, Barbeiro, Admin, Permissao, Venda, Agendamento
from app.utils import admin_required, save_picture, allowed_file

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Contagem de usuários por tipo
    total_clientes = Cliente.query.count()
    total_barbeiros = Barbeiro.query.count()
    barbeiros_ativos = Barbeiro.query.filter_by(ativo=True).count()
    
    # Dados para gráficos
    agendamentos_hoje = Agendamento.query.filter(
        Agendamento.data_hora >= datetime.today().replace(hour=0, minute=0, second=0),
        Agendamento.data_hora <= datetime.today().replace(hour=23, minute=59, second=59)
    ).count()
    
    # Lista dos últimos agendamentos
    ultimos_agendamentos = Agendamento.query.order_by(Agendamento.data_criacao.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                          total_clientes=total_clientes,
                          total_barbeiros=total_barbeiros,
                          barbeiros_ativos=barbeiros_ativos,
                          agendamentos_hoje=agendamentos_hoje,
                          ultimos_agendamentos=ultimos_agendamentos)

@admin_bp.route('/usuarios')
@login_required
@admin_required
def usuarios():
    tipo_filtro = request.args.get('tipo', 'todos')
    
    if tipo_filtro == 'clientes':
        usuarios = Cliente.query.order_by(Cliente.nome).all()
    elif tipo_filtro == 'barbeiros':
        usuarios = Barbeiro.query.order_by(Barbeiro.nome).all()
    elif tipo_filtro == 'admins':
        usuarios = Admin.query.order_by(Admin.nome).all()
    else:
        usuarios = User.query.order_by(User.nome).all()
    
    return render_template('admin/usuarios.html', usuarios=usuarios, tipo_filtro=tipo_filtro)

@admin_bp.route('/usuarios/<string:user_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_usuario(user_id):
    usuario = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        usuario.nome = request.form.get('nome')
        email = request.form.get('email')
        
        # Verificar se o email já está em uso por outro usuário
        if email != usuario.email and User.query.filter_by(email=email).first():
            flash('Este email já está em uso por outro usuário!', 'danger')
            return redirect(url_for('admin.editar_usuario', user_id=user_id))
            
        usuario.email = email
        
        # Atualização de senha (se fornecida)
        nova_senha = request.form.get('nova_senha')
        if nova_senha and nova_senha.strip():
            usuario.set_password(nova_senha)
            
        # Atualização de dados específicos por tipo de usuário
        if usuario.tipo in ['cliente', 'barbeiro']:
            numero_aluno = request.form.get('numero_aluno')
            if usuario.tipo == 'cliente':
                cliente = Cliente.query.get(usuario.id)
                cliente.numero_aluno = numero_aluno
            else:
                barbeiro = Barbeiro.query.get(usuario.id)
                barbeiro.numero_aluno = numero_aluno
                barbeiro.ativo = 'ativo' in request.form
        
        # Upload de foto de perfil
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '' and allowed_file(file.filename):
                foto_perfil = save_picture(file)
                usuario.foto_perfil = foto_perfil
        
        db.session.commit()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('admin.usuarios'))
    
    return render_template('admin/editar_usuario.html', usuario=usuario)

@admin_bp.route('/usuarios/<string:user_id>/excluir', methods=['POST'])
@login_required
@admin_required
def excluir_usuario(user_id):
    usuario = User.query.get_or_404(user_id)
    
    # Não permite excluir o próprio usuário administrador
    if usuario.id == current_user.id:
        flash('Você não pode excluir sua própria conta!', 'danger')
        return redirect(url_for('admin.usuarios'))
    
    # Excluir relacionamentos conforme o tipo de usuário
    if usuario.tipo == 'cliente':
        Agendamento.query.filter_by(cliente_id=usuario.id).delete()
        Venda.query.filter_by(cliente_id=usuario.id).delete()
    elif usuario.tipo == 'barbeiro':
        Agendamento.query.filter_by(barbeiro_id=usuario.id).delete()
        Venda.query.filter_by(barbeiro_id=usuario.id).delete()
        Permissao.query.filter_by(barbeiro_id=usuario.id).delete()
    
    db.session.delete(usuario)
    db.session.commit()
    
    flash('Usuário excluído com sucesso!', 'success')
    return redirect(url_for('admin.usuarios'))

@admin_bp.route('/permissoes')
@login_required
@admin_required
def permissoes():
    barbeiros = Barbeiro.query.all()
    return render_template('admin/permissoes.html', barbeiros=barbeiros)

@admin_bp.route('/permissoes/<string:barbeiro_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_permissao(barbeiro_id):
    barbeiro = Barbeiro.query.get_or_404(barbeiro_id)
    
    # Inverte o estado de ativação do barbeiro
    barbeiro.ativo = not barbeiro.ativo
    
    # Atualiza ou cria a permissão
    permissao = Permissao.query.filter_by(barbeiro_id=barbeiro_id).first()
    if permissao:
        permissao.ativo = barbeiro.ativo
    else:
        nova_permissao = Permissao(barbeiro_id=barbeiro_id, ativo=barbeiro.ativo)
        db.session.add(nova_permissao)
    
    db.session.commit()
    
    status = 'ativado' if barbeiro.ativo else 'desativado'
    flash(f'Barbeiro {barbeiro.nome} {status} com sucesso!', 'success')
    
    return redirect(url_for('admin.permissoes'))

@admin_bp.route('/adicionar-admin', methods=['GET', 'POST'])
@login_required
@admin_required
def adicionar_admin():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        # Validações
        if User.query.filter_by(email=email).first():
            flash('Este email já está em uso!', 'danger')
            return redirect(url_for('admin.adicionar_admin'))
            
        # Upload da foto de perfil
        foto_perfil = 'default.jpg'
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '' and allowed_file(file.filename):
                foto_perfil = save_picture(file)
        
        # Criação do administrador
        novo_admin = Admin(nome=nome, email=email, foto_perfil=foto_perfil)
        novo_admin.set_password(senha)
        
        db.session.add(novo_admin)
        db.session.commit()
        
        flash('Administrador adicionado com sucesso!', 'success')
        return redirect(url_for('admin.usuarios'))
        
    return render_template('admin/adicionar_admin.html')
