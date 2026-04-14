from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
import os


def generar_setlist(setlist, group):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch
    )

    COLOR_FONDO      = colors.HexColor('#1a1a2e')
    COLOR_ACENTO     = colors.HexColor('#e94560')
    COLOR_SECUNDARIO = colors.HexColor('#0f3460')
    COLOR_BLANCO     = colors.white
    COLOR_GRIS       = colors.HexColor('#aaaaaa')

    estilos = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        'titulo',
        fontSize=28, textColor=COLOR_ACENTO,
        alignment=TA_CENTER, fontName='Helvetica-Bold',
        spaceAfter=6, spaceBefore=0
    )
    estilo_subtitulo = ParagraphStyle(
        'subtitulo',
        fontSize=14, textColor=COLOR_BLANCO,
        alignment=TA_CENTER, fontName='Helvetica',
        spaceAfter=4, spaceBefore=0
    )
    estilo_evento = ParagraphStyle(
        'evento',
        fontSize=11, textColor=COLOR_GRIS,
        alignment=TA_CENTER, fontName='Helvetica-Oblique',
        spaceAfter=0, spaceBefore=0
    )

    elementos = []

    # --- LOGO ---
    if group.logo_path:
        ruta_logo = os.path.join('static', group.logo_path)
        if os.path.exists(ruta_logo):
            try:
                logo = Image(ruta_logo, width=1.0*inch, height=1.0*inch)
                logo.hAlign = 'CENTER'
                elementos.append(logo)
            except Exception:
                pass

    # --- ENCABEZADO: cada elemento por separado con Spacer controlado ---
    elementos.append(Spacer(1, 8))
    elementos.append(Paragraph(group.group_name, estilo_titulo))
    elementos.append(Spacer(1, 4))
    elementos.append(Paragraph('SETLIST', estilo_subtitulo))
    elementos.append(Spacer(1, 4))
    elementos.append(Paragraph(setlist.event_name, estilo_evento))
    elementos.append(Spacer(1, 0.25 * inch))

    # --- TABLA ---
    encabezado = ['#', 'CANCIÓN', 'GÉNERO', 'TONO', 'CANTANTE']
    filas = [encabezado]

    for entrada in setlist.songs:
        cancion = entrada.song
        filas.append([
            str(entrada.position),
            cancion.title,
            cancion.genre,
            cancion.key,
            cancion.singer
        ])

    tabla = Table(filas, colWidths=[
        0.4 * inch,
        2.4 * inch,
        1.4 * inch,
        0.8 * inch,
        1.6 * inch
    ])

    estilo_tabla = TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0), COLOR_ACENTO),
        ('TEXTCOLOR',    (0, 0), (-1, 0), COLOR_BLANCO),
        ('FONTNAME',     (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',     (0, 0), (-1, 0), 10),
        ('ALIGN',        (0, 0), (-1, 0), 'CENTER'),
        ('TOPPADDING',   (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING',(0, 0), (-1, 0), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [
            colors.HexColor('#16213e'),
            colors.HexColor('#0f3460')
        ]),
        ('TEXTCOLOR',    (0, 1), (-1, -1), COLOR_BLANCO),
        ('FONTNAME',     (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',     (0, 1), (-1, -1), 10),
        ('TOPPADDING',   (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING',(0, 1), (-1, -1), 8),
        ('ALIGN',        (0, 1), (0, -1),  'CENTER'),
        ('GRID',         (0, 0), (-1, -1), 0.5, colors.HexColor('#2a2a4a')),
        ('LINEBELOW',    (0, 0), (-1, 0),  1.5, COLOR_ACENTO),
    ])

    tabla.setStyle(estilo_tabla)
    elementos.append(tabla)

    # --- PIE ---
    elementos.append(Spacer(1, 0.3 * inch))
    estilo_pie = ParagraphStyle(
        'pie', fontSize=8, textColor=COLOR_GRIS,
        alignment=TA_CENTER, fontName='Helvetica-Oblique'
    )
    total = len(setlist.songs)
    elementos.append(Paragraph(
        f'{total} canción{"es" if total != 1 else ""} · Generado con Repertorio App',
        estilo_pie
    ))

    doc.build(elementos)
    return buffer.getvalue()