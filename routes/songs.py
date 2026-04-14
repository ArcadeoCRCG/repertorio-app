from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Song

songs_bp = Blueprint('songs', __name__)


@songs_bp.route('/canciones')
@login_required
def index():
    # Leer filtros del buscador (vienen por URL: /canciones?genre=Rock)
    genre_filter  = request.args.get('genre',  '').strip()
    singer_filter = request.args.get('singer', '').strip()

    # Empezamos la consulta filtrando SIEMPRE por el grupo actual
    # Esto es clave en el modelo SaaS: cada grupo solo ve sus canciones
    query = Song.query.filter_by(group_id=current_user.id)

    if genre_filter:
        query = query.filter(Song.genre.ilike(f'%{genre_filter}%'))

    if singer_filter:
        query = query.filter(Song.singer.ilike(f'%{singer_filter}%'))

    songs = query.order_by(Song.title).all()

    # Obtener géneros y cantantes únicos para los desplegables del buscador
    all_songs = Song.query.filter_by(group_id=current_user.id).all()
    genres  = sorted(set(s.genre  for s in all_songs))
    singers = sorted(set(s.singer for s in all_songs))

    return render_template('songs/index.html',
        songs=songs,
        genres=genres,
        singers=singers,
        genre_filter=genre_filter,
        singer_filter=singer_filter
    )


@songs_bp.route('/canciones/nueva', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title  = request.form.get('title',  '').strip()
        genre  = request.form.get('genre',  '').strip()
        key    = request.form.get('key',    '').strip()
        singer = request.form.get('singer', '').strip()

        # Validación básica
        if not all([title, genre, key, singer]):
            flash('Todos los campos son obligatorios', 'error')
            return render_template('songs/form.html', song=None)

        nueva = Song(
            group_id = current_user.id,
            title    = title,
            genre    = genre,
            key      = key,
            singer   = singer
        )
        db.session.add(nueva)
        db.session.commit()
        flash(f'"{title}" agregada al repertorio ✓', 'success')
        return redirect(url_for('songs.index'))

    return render_template('songs/form.html', song=None)


@songs_bp.route('/canciones/editar/<int:song_id>', methods=['GET', 'POST'])
@login_required
def edit(song_id):
    # filter_by con group_id garantiza que nadie edite canciones ajenas
    song = Song.query.filter_by(id=song_id, group_id=current_user.id).first_or_404()

    if request.method == 'POST':
        song.title  = request.form.get('title',  '').strip()
        song.genre  = request.form.get('genre',  '').strip()
        song.key    = request.form.get('key',    '').strip()
        song.singer = request.form.get('singer', '').strip()

        if not all([song.title, song.genre, song.key, song.singer]):
            flash('Todos los campos son obligatorios', 'error')
            return render_template('songs/form.html', song=song)

        db.session.commit()
        flash(f'"{song.title}" actualizada ✓', 'success')
        return redirect(url_for('songs.index'))

    return render_template('songs/form.html', song=song)


@songs_bp.route('/canciones/eliminar/<int:song_id>', methods=['POST'])
@login_required
def delete(song_id):
    song = Song.query.filter_by(id=song_id, group_id=current_user.id).first_or_404()
    titulo = song.title
    db.session.delete(song)
    db.session.commit()
    flash(f'"{titulo}" eliminada del repertorio', 'success')
    return redirect(url_for('songs.index'))