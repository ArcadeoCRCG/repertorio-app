from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db, Group
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Crear carpeta de uploads si no existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Inicializar la base de datos
    db.init_app(app)

    # Inicializar el manejador de login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'        # si no está logueado, manda aquí
    login_manager.login_message = 'Inicia sesión para continuar'

    @login_manager.user_loader
    def load_user(user_id):
        """Flask-Login usa esto para saber quién está logueado"""
        return Group.query.get(int(user_id))

    # Registrar los blueprints (rutas separadas por módulo)
    from routes.auth    import auth_bp
    from routes.songs   import songs_bp
    from routes.settings import settings_bp
    from routes.setlist import setlist_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(songs_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(setlist_bp)

    # Crear todas las tablas al iniciar
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)