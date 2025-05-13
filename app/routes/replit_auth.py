import jwt
import os
import uuid
from urllib.parse import urlencode
from flask import Blueprint, g, session, redirect, request, url_for
from flask_dance.consumer import OAuth2ConsumerBlueprint, oauth_authorized, oauth_error
from flask_dance.consumer.storage import BaseStorage
from flask_login import login_user, logout_user, current_user
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
from sqlalchemy.exc import NoResultFound
from werkzeug.local import LocalProxy
from werkzeug.security import generate_password_hash

from app import db
from app.models.models import User, Cliente, OAuth

class UserSessionStorage(BaseStorage):
    def get(self, blueprint):
        try:
            token = db.session.query(OAuth).filter_by(
                user_id=current_user.get_id(),
                browser_session_key=g.browser_session_key,
                provider=blueprint.name,
            ).one().token
        except NoResultFound:
            token = None
        return token

    def set(self, blueprint, token):
        db.session.query(OAuth).filter_by(
            user_id=current_user.get_id(),
            browser_session_key=g.browser_session_key,
            provider=blueprint.name,
        ).delete()
        new_model = OAuth(
            user_id=current_user.get_id(),
            browser_session_key=g.browser_session_key,
            provider=blueprint.name,
            token=token
        )
        db.session.add(new_model)
        db.session.commit()

    def delete(self, blueprint):
        db.session.query(OAuth).filter_by(
            user_id=current_user.get_id(),
            browser_session_key=g.browser_session_key,
            provider=blueprint.name).delete()
        db.session.commit()

def make_replit_blueprint():
    try:
        repl_id = os.environ.get('REPL_ID', 'default-repl-id')
    except KeyError:
        # Use um valor padrão para desenvolvimento local
        repl_id = 'default-repl-id'

    issuer_url = os.environ.get('ISSUER_URL', "https://replit.com/oidc")

    replit_bp = OAuth2ConsumerBlueprint(
        "replit_auth",
        __name__,
        client_id=repl_id,
        client_secret=None,
        base_url=issuer_url,
        authorization_url_params={
            "prompt": "login consent",
        },
        token_url=issuer_url + "/token",
        token_url_params={
            "auth": (),
            "include_client_id": True,
        },
        auto_refresh_url=issuer_url + "/token",
        auto_refresh_kwargs={
            "client_id": repl_id,
        },
        authorization_url=issuer_url + "/auth",
        use_pkce=True,
        code_challenge_method="S256",
        scope=["openid", "profile", "email", "offline_access"],
        storage=UserSessionStorage(),
    )

    @replit_bp.before_app_request
    def set_applocal_session():
        if '_browser_session_key' not in session:
            session['_browser_session_key'] = uuid.uuid4().hex
        session.modified = True
        g.browser_session_key = session['_browser_session_key']
        g.flask_dance_replit = replit_bp.session

    @replit_bp.route("/logout")
    def logout():
        del replit_bp.token
        logout_user()

        end_session_endpoint = issuer_url + "/session/end"
        encoded_params = urlencode({
            "client_id": repl_id,
            "post_logout_redirect_uri": request.url_root,
        })
        logout_url = f"{end_session_endpoint}?{encoded_params}"

        return redirect(logout_url)

    return replit_bp

def save_user(user_claims):
    # Verifica se já existe um usuário
    existing_user = User.query.filter_by(id=user_claims['sub']).first()
    
    if existing_user:
        # Atualiza informações existentes
        existing_user.email = user_claims.get('email')
        existing_user.nome = f"{user_claims.get('first_name', '')} {user_claims.get('last_name', '')}".strip() or "Usuário Replit"
        existing_user.foto_perfil = user_claims.get('profile_image_url', 'default.jpg')
        db.session.commit()
        return existing_user
    
    # Cria um novo usuário como cliente por padrão
    from werkzeug.security import generate_password_hash
    import secrets
    import uuid
    
    # Gera um nome de usuário único baseado no ID do Replit ou nome de usuário
    nome_usuario = f"{user_claims.get('first_name', 'user')}{uuid.uuid4().hex[:6]}".lower()
    
    novo_usuario = Cliente(
        id=user_claims['sub'],
        username=nome_usuario,
        email=user_claims.get('email'),
        nome=f"{user_claims.get('first_name', '')} {user_claims.get('last_name', '')}".strip() or "Usuário Replit",
        foto_perfil=user_claims.get('profile_image_url', 'default.jpg'),
        tipo='cliente',
        senha_hash=generate_password_hash(secrets.token_hex(16))
    )
    
    db.session.add(novo_usuario)
    db.session.commit()
    
    return novo_usuario

@oauth_authorized.connect
def logged_in(blueprint, token):
    from urllib.parse import urlencode
    
    user_claims = jwt.decode(token['id_token'],
                           options={"verify_signature": False})
    user = save_user(user_claims)
    login_user(user)
    blueprint.token = token
    next_url = session.pop("next_url", None)
    if next_url is not None:
        return redirect(next_url)

@oauth_error.connect
def handle_error(blueprint, error, error_description=None, error_uri=None):
    return redirect(url_for('auth.login'))

replit_auth_bp = make_replit_blueprint()