from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Group(UserMixin, db.Model):
    """
    Representa a cada cliente/grupo musical.
    UserMixin le da los métodos que Flask-Login necesita
    (is_authenticated, is_active, get_id, etc.)
    """
    __tablename__ = 'groups'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    group_name    = db.Column(db.String(120), nullable=False, default='Mi Grupo')
    logo_path     = db.Column(db.String(256), nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones: un grupo tiene muchas canciones
    songs    = db.relationship('Song',    backref='group', lazy=True, cascade='all, delete-orphan')
    setlists = db.relationship('Setlist', backref='group', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Encripta la contraseña antes de guardarla"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica si la contraseña ingresada coincide"""
        return check_password_hash(self.password_hash, password)


class Song(db.Model):
    """Una canción del repertorio de un grupo"""
    __tablename__ = 'songs'

    id         = db.Column(db.Integer, primary_key=True)
    group_id   = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    title      = db.Column(db.String(150), nullable=False)
    genre      = db.Column(db.String(80),  nullable=False)
    key        = db.Column(db.String(20),  nullable=False)  # tono
    singer     = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación con setlist_songs
    setlist_entries = db.relationship('SetlistSong', backref='song', lazy=True, cascade='all, delete-orphan')


class Setlist(db.Model):
    """Un setlist generado para una presentación"""
    __tablename__ = 'setlists'

    id         = db.Column(db.Integer, primary_key=True)
    group_id   = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    event_name = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Un setlist tiene varias canciones en orden
    songs = db.relationship('SetlistSong', backref='setlist', lazy=True,
                             order_by='SetlistSong.position', cascade='all, delete-orphan')


class SetlistSong(db.Model):
    """
    Tabla intermedia: qué canciones tiene un setlist y en qué posición.
    Esto permite que el usuario ordene las canciones a su gusto.
    """
    __tablename__ = 'setlist_songs'

    id         = db.Column(db.Integer, primary_key=True)
    setlist_id = db.Column(db.Integer, db.ForeignKey('setlists.id'), nullable=False)
    song_id    = db.Column(db.Integer, db.ForeignKey('songs.id'),    nullable=False)
    position   = db.Column(db.Integer, nullable=False)  # 1, 2, 3...


# --- MODELOS PREPARADOS PARA FASES FUTURAS ---

class Member(db.Model):
    """FASE 3: Integrantes del grupo"""
    __tablename__ = 'members'

    id         = db.Column(db.Integer, primary_key=True)
    group_id   = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    name       = db.Column(db.String(100), nullable=False)
    role       = db.Column(db.String(80),  nullable=True)   # ej: guitarra, voz, batería
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Event(db.Model):
    """FASE 2: Fechas y presentaciones"""
    __tablename__ = 'events'

    id         = db.Column(db.Integer, primary_key=True)
    group_id   = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    event_name = db.Column(db.String(150), nullable=False)
    event_date = db.Column(db.DateTime,    nullable=False)
    venue      = db.Column(db.String(200), nullable=True)
    notes      = db.Column(db.Text,        nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)