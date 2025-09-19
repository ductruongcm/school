from app.schemas import Class_room, Year, Teachers, Users
from app.extensions import db

def db_add_class(class_room, year):
    year = Year.query.filter(Year.year == year).first()
    if year:
        new_class = Class_room(class_room = class_room, year_id = year.id)
    db.session.add(new_class)
    db.session.commit()

def db_show_class(current_year, username, role):
    year = Year.query.filter(Year.year == current_year).first()
    if role == 'admin':
        class_room = Class_room.query.filter(Class_room.year_id == year.id, 
                                             Class_room.status == True).all()
        data = [data.class_room for data in class_room]
    else:
        user_id = Users.query.filter(Users.username == username).first().id
        class_room_id = Teachers.query.filter(Teachers.user_id == user_id).first().class_room_id
        data = [Class_room.query.filter(year.id == Class_room.year_id, Class_room.status == True, Class_room.id == class_room_id).first().class_room]
    return data
