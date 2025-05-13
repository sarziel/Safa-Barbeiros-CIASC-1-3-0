from flask import Blueprint, render_template, redirect, url_for, current_app, send_from_directory
from flask_login import current_user

common_bp = Blueprint('common', __name__)

@common_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.tipo == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.tipo == 'barbeiro':
            return redirect(url_for('barbeiro.dashboard'))
        elif current_user.tipo == 'cliente':
            return redirect(url_for('cliente.dashboard'))
    
    return redirect(url_for('auth.login'))

@common_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
