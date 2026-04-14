from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from models import Group

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Buscar el grupo por username
        group = Group.query.filter_by(username=username).first()

        if group and group.check_password(password):
            # Login exitoso: Flask-Login guarda la sesión
            login_user(group)
            return redirect(url_for('songs.index'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))