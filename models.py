# models.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# IMPORTANT: db lives here now (not in app.py)
db = SQLAlchemy()

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(160))
    city = db.Column(db.String(120))
    message = db.Column(db.Text)
    source = db.Column(db.String(32), default="website")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def as_lines(self):
        return [
            f"Name: {self.name}",
            f"Phone: {self.phone}",
            f"Email: {self.email or '-'}",
            f"City: {self.city or '-'}",
            f"Message: {self.message or '-'}",
            f"Source: {self.source}",
        ]
