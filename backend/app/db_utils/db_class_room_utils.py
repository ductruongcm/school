from app.schemas import Class_room, Year
from app.extensions import db

def db_add_class(class_room, year):
    year = Year.query.filter(Year.year == year).first()
    if year:
        new_class = Class_room(class_room = class_room, year_id = year.id)
    db.session.add(new_class)
    db.session.commit()

def db_show_class(current_year):
    year = Year.query.filter(Year.year == current_year).first()
    rows = db.session.query(Class_room.class_room, 
                            Class_room.qty).filter(year.id == Class_room.year_id, 
                                                   Class_room.status == True).order_by(Class_room.class_room).all()
    keys = ['class_room', 'qty']
    return [dict(zip(keys, row)) for row in rows]
