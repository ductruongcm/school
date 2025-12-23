from app import launch
from app.extensions import db

app = launch()

with app.app_context():
    db.create_all()
    print('Database migrated successfully!')
