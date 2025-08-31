from app import launch
from app.extensions import db
from app.schemas import User

def create_table():
    app = launch()
    with app.app_context():
        db.create_all()
        db.session.commit()
    return print('Created table(s) successfully')
