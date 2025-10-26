# init_db.py
import os
from app import create_app
from models import db

print("Starting database initialization...")
app = create_app()
with app.app_context():
    print("Creating all database tables...")
    db.create_all()
    print("Database tables created.")