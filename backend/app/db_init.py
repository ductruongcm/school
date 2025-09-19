from app import launch
from app.extensions import db
from app.schemas import Monitoring
# from app.routes.class_room.schemas import class_schemas


def create_table():
    app = launch()
    with app.app_context():
        db.create_all()
        db.session.commit()
    return print('Created table(s) successfully')
