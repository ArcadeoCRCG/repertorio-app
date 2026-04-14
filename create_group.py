from app import create_app
from models import db, Group

app = create_app()

with app.app_context():
    # Cambia estos datos a los que quieras
    nuevo_grupo = Group(
        username='grupodharma',
        group_name='Grupo Dharma'
    )
    nuevo_grupo.set_password('12345')  # contraseña encriptada automáticamente

    db.session.add(nuevo_grupo)
    db.session.commit()
    print(f'Grupo creado: {nuevo_grupo.username} / ID: {nuevo_grupo.id}')