# manage.py
from flask.cli import FlaskGroup
from flask_migrate import Migrate
from models import db
from app import create_app

app = create_app()
migrate = Migrate(app, db)
cli = FlaskGroup(create_app=lambda: app)

@app.cli.command("db_init")
def db_init():
    """Optional: create tables without Alembic (rarely needed)."""
    with app.app_context():
        db.create_all()
        print("✅ Database initialized.")

if __name__ == "__main__":
    cli()
