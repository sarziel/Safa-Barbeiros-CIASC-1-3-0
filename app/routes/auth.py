import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models.models import User, Cliente, Barbeiro, Admin
from app.utils import allowed_file, save_picture

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.tipo == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.tipo == 'barbeiro':
            return redirect(url_for('barbeiro.dashboard'))
        elif current_user.tipo == 'cliente':
            return redirect(url_for('cliente.dashboard'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        user = User.query.filter_by(email=email).first()
        
        if user is None or not user.check_password(senha):
            flash('Email ou senha incorretos. Tente novamente.', 'danger')
            return redirect(url_for('auth.login'))
            
        # Verifica se o barbeiro está ativo
        if user.tipo == 'barbeiro':
            barbeiro = Barbeiro.query.get(user.id)
            if not barbeiro.ativo:
                flash('Sua conta está inativa. Entre em contato com o administrador.', 'warning')
                return redirect(url_for('auth.login'))
        
        login_user(user)
        next_page = request.args.get('next')
        
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('auth.index')
            
        flash(f'Bem-vindo(a), {user.nome}!', 'success')
        return redirect(next_page)
        
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu com sucesso!', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
        
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        senha_confirmacao = request.form.get('senha_confirmacao')
        tipo = request.form.get('tipo')
        numero_aluno = request.form.get('numero_aluno', None)
        
        # Validações
        if senha != senha_confirmacao:
            flash('As senhas não correspondem!', 'danger')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(email=email).first():
            flash('Este email já está em uso. Faça login ou recupere sua senha.', 'danger')
            return redirect(url_for('auth.register'))
            
        if tipo not in ['cliente', 'barbeiro']:
            flash('Tipo de usuário inválido!', 'danger')
            return redirect(url_for('auth.register'))
        
        # Upload da foto de perfil
        foto_perfil = 'default.jpg'
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '' and allowed_file(file.filename):
                foto_perfil = save_picture(file)
        
        # Criação do usuário
        if tipo == 'cliente':
            novo_usuario = Cliente(nome=nome, email=email, numero_aluno=numero_aluno, foto_perfil=foto_perfil)
        else:  # tipo == 'barbeiro'
            novo_usuario = Barbeiro(nome=nome, email=email, numero_aluno=numero_aluno, foto_perfil=foto_perfil, ativo=False)
            # Criar permissão para o barbeiro
            permissao = Permissao(barbeiro_id=novo_usuario.id, ativo=False)
            db.session.add(permissao)
        
        novo_usuario.set_password(senha)
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        if tipo == 'barbeiro':
            flash('Registro realizado com sucesso! Sua conta precisa ser ativada por um administrador.', 'info')
        else:
            flash('Registro realizado com sucesso! Faça login para continuar.', 'success')
            
        return redirect(url_for('auth.login'))
        
    return render_template('register.html')

@auth_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha_atual = request.form.get('senha_atual')
        nova_senha = request.form.get('nova_senha')
        
        # Validação do email
        if email != current_user.email and User.query.filter_by(email=email).first():
            flash('Este email já está em uso!', 'danger')
            return redirect(url_for('auth.perfil'))
            
        # Atualização de senha
        if senha_atual and nova_senha:
            if not current_user.check_password(senha_atual):
                flash('Senha atual incorreta!', 'danger')
                return redirect(url_for('auth.perfil'))
            current_user.set_password(nova_senha)
            flash('Senha atualizada com sucesso!', 'success')
            
        # Atualização dos dados básicos
        current_user.nome = nome
        current_user.email = email
        
        # Upload de nova foto de perfil
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '' and allowed_file(file.filename):
                foto_perfil = save_picture(file)
                
                # Remove a foto antiga se não for a default
                if current_user.foto_perfil != 'default.jpg':
                    old_file = os.path.join(current_app.config['UPLOAD_FOLDER'], current_user.foto_perfil)
                    if os.path.exists(old_file):
                        os.remove(old_file)
                        
                current_user.foto_perfil = foto_perfil
        
        # Atualização de dados específicos por tipo de usuário
        if current_user.tipo in ['cliente', 'barbeiro']:
            numero_aluno = request.form.get('numero_aluno')
            if current_user.tipo == 'cliente':
                cliente = Cliente.query.get(current_user.id)
                cliente.numero_aluno = numero_aluno
            else:
                barbeiro = Barbeiro.query.get(current_user.id)
                barbeiro.numero_aluno = numero_aluno
        
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('auth.perfil'))
        
    return render_template('perfil.html', user=current_user)

# Importação para evitar erro de referência circular
from app.models.models import Permissao
