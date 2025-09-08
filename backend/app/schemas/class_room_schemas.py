from app.extensions import db
# from app.schemas import Students, Cloud

class Year(db.Model):
    __tablename__ = 'year'
    id = db.Column(db.Integer, primary_key = True)
    year = db.Column(db.String, unique = True, nullable = False)
    class_room = db.relationship('Class_room', back_populates = 'year', lazy = True)

class Class_room(db.Model):
    __tablename__ = 'class_room'
    id = db.Column(db.Integer, primary_key = True)
    year_id = db.Column(db.Integer, db.ForeignKey('year.id', ondelete = 'CASCADE'))
    class_room = db.Column(db.String, unique = True, nullable = False)
    qty = db.Column(db.Integer, default = 0)
    status = db.Column(db.Boolean, default = True)
    year = db.relationship('Year', back_populates = 'class_room', lazy = True)
    students = db.relationship('Students', back_populates = 'class_room', lazy = True)
    cloud = db.relationship('Cloud', back_populates = 'class_room', lazy = True)
    info = db.relationship("Info", back_populates = 'class_room', lazy = True)
