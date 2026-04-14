from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from models import db, Song, Setlist, SetlistSong
from io import BytesIO
import pdf_generator

setlist_bp = Blueprint('setlist', __name__)


@setlist_bp.route('/setlist')
@login_required
def index():
    # Todas las canciones del grupo para mostrar en el selector
    songs = Song.query.filter_by(group_id=current_user.id).order_by(Song.title).all()
    # Historial de setlists generados
    setlists = Setlist.query.filter_by(group_id=current_user.id)\
                            .order_by(Setlist.created_at.desc()).all()
    return render_template('setlist/index.html', songs=songs, setlists=setlists)


@setlist_bp.route('/setlist/generar', methods=['POST'])
@login_required
def generate():
    event_name  = request.form.get('event_name', '').strip()
    # song_ids viene como lista: ['3','1','7'] en el orden que el usuario definió
    song_ids    = request.form.getlist('song_ids')

    if not event_name:
        flash('Escribe el nombre del evento', 'error')
        return redirect(url_for('setlist.index'))

    if not song_ids:
        flash('Selecciona al menos una canción', 'error')
        return redirect(url_for('setlist.index'))

    # Guardar el setlist en la BD
    nuevo_setlist = Setlist(group_id=current_user.id, event_name=event_name)
    db.session.add(nuevo_setlist)
    db.session.flush()  # flush para obtener el ID sin hacer commit todavía

    for posicion, song_id in enumerate(song_ids, start=1):
        song = Song.query.filter_by(id=int(song_id), group_id=current_user.id).first()
        if song:
            entrada = SetlistSong(
                setlist_id = nuevo_setlist.id,
                song_id    = song.id,
                position   = posicion
            )
            db.session.add(entrada)

    db.session.commit()
    flash(f'Setlist "{event_name}" guardado ✓', 'success')
    return redirect(url_for('setlist.preview', setlist_id=nuevo_setlist.id))


@setlist_bp.route('/setlist/<int:setlist_id>')
@login_required
def preview(setlist_id):
    setlist = Setlist.query.filter_by(id=setlist_id, group_id=current_user.id).first_or_404()
    return render_template('setlist/preview.html', setlist=setlist)


@setlist_bp.route('/setlist/<int:setlist_id>/pdf')
@login_required
def download_pdf(setlist_id):
    setlist = Setlist.query.filter_by(id=setlist_id, group_id=current_user.id).first_or_404()

    # Generar el PDF en memoria (no se guarda en disco)
    pdf_bytes = pdf_generator.generar_setlist(setlist, current_user)

    return send_file(
        BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=False,  # False = abre en el navegador, True = descarga
        download_name=f'setlist_{setlist.event_name}.pdf'
    )


@setlist_bp.route('/setlist/<int:setlist_id>/eliminar', methods=['POST'])
@login_required
def delete(setlist_id):
    setlist = Setlist.query.filter_by(id=setlist_id, group_id=current_user.id).first_or_404()
    db.session.delete(setlist)
    db.session.commit()
    flash('Setlist eliminado', 'success')
    return redirect(url_for('setlist.index'))