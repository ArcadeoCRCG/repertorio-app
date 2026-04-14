from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from models import db
from werkzeug.utils import secure_filename
import os

settings_bp = Blueprint('settings', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@settings_bp.route('/configuracion', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        action = request.form.get('action')

        # --- ACTUALIZAR NOMBRE DEL GRUPO ---
        if action == 'update_name':
            nuevo_nombre = request.form.get('group_name', '').strip()
            if not nuevo_nombre:
                flash('El nombre no puede estar vacío', 'error')
            else:
                current_user.group_name = nuevo_nombre
                db.session.commit()
                flash('Nombre actualizado ✓', 'success')

        # --- SUBIR LOGO ---
        elif action == 'upload_logo':
            if 'logo' not in request.files:
                flash('No se seleccionó ningún archivo', 'error')
            else:
                file = request.files['logo']
                if file.filename == '':
                    flash('No se seleccionó ningún archivo', 'error')
                elif not allowed_file(file.filename):
                    flash('Formato no válido. Usa PNG, JPG, GIF o WEBP', 'error')
                else:
                    # Nombre único para evitar colisiones entre grupos
                    ext      = file.filename.rsplit('.', 1)[1].lower()
                    filename = f'logo_{current_user.id}.{ext}'
                    ruta = os.path.join('static', 'uploads', filename)

                    # Borrar logo anterior si existe
                    if current_user.logo_path:
                        ruta_anterior = os.path.join('static', current_user.logo_path)
                        if os.path.exists(ruta_anterior):
                            os.remove(ruta_anterior)

                    file.save(ruta)
                    # Guardamos solo la ruta relativa a /static/
                    current_user.logo_path = f'uploads/{filename}'
                    db.session.commit()
                    flash('Logo actualizado ✓', 'success')

        # --- ELIMINAR LOGO ---
        elif action == 'delete_logo':
            if current_user.logo_path:
                ruta = os.path.join('static', current_user.logo_path)
                if os.path.exists(ruta):
                    os.remove(ruta)
                current_user.logo_path = None
                db.session.commit()
                flash('Logo eliminado', 'success')

        # --- CAMBIAR CONTRASEÑA ---
        elif action == 'change_password':
            actual  = request.form.get('current_password', '')
            nueva   = request.form.get('new_password', '')
            repetir = request.form.get('repeat_password', '')

            if not current_user.check_password(actual):
                flash('La contraseña actual es incorrecta', 'error')
            elif len(nueva) < 4:
                flash('La nueva contraseña debe tener al menos 4 caracteres', 'error')
            elif nueva != repetir:
                flash('Las contraseñas no coinciden', 'error')
            else:
                current_user.set_password(nueva)
                db.session.commit()
                flash('Contraseña actualizada ✓', 'success')

        return redirect(url_for('settings.index'))

    return render_template('settings/index.html')