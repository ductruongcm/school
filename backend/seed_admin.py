from app.extensions import db
from app.models import Users
from main import launch
from werkzeug.security import generate_password_hash

app = launch()

with app.app_context():
    if not Users.query.filter(Users.username == 'administrator').first():
        admin = Users(username = 'administrator',
                      password = generate_password_hash('#Adm1n01'),
                      role = 'admin')
        
        db.session.add(admin)
        db.session.commit()
        print('Admin user created!')
    else:
        print('Admin user already exists!')
